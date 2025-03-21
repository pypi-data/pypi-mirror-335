# file: event_map.py

import folium
import pandas as pd
import numpy as np
import math
import logging
import html
import branca
import matplotlib.pyplot as plt

import geopandas as gpd
from geopy.distance import geodesic
from folium import plugins
from folium.plugins import MarkerCluster

from .config import (
    MapConfig, EventConfig, FaultConfig, StationConfig,
    TILE_LAYERS, TILE_LAYER_CONFIGS, EARTH_RADIUS_KM
)
from .utils import (
    convert_xy_to_latlon, 
    calculate_distances_vectorized,
    load_faults,
    load_stations_csv
)

logger = logging.getLogger(__name__)

class EventMap:
    """
    Builds a map from events.csv + legend.csv, supporting lat/lon or x/y,
    mandatory magnitude column, optional distance calc, heatmap, color scale,
    epicentral distance circles, faults, stations, multiple tile layers.
    """

    def __init__(
        self,
        map_config: MapConfig,
        event_config: EventConfig,
        events_csv: str,
        legend_csv: str,
        x_col: str = None,
        y_col: str = None,
        location_crs: str = 'EPSG:4326',
        mandatory_mag_col: str = 'mag',
        calculate_distance: bool = True,
        fault_config: FaultConfig = None,
        station_config: StationConfig = None,
        log_level=logging.INFO
    ):
        logger.setLevel(log_level)
        self.map_config = map_config
        self.event_config = event_config
        self.fault_config = fault_config
        self.station_config = station_config

        self.events_csv = events_csv
        self.legend_csv = legend_csv
        self.x_col = x_col
        self.y_col = y_col
        self.location_crs = location_crs
        self.mandatory_mag_col = mandatory_mag_col
        self.calculate_distance = calculate_distance

        # Data
        self.events_df = pd.DataFrame()
        self.legend_df = pd.DataFrame()
        self.stations_df = pd.DataFrame()
        self.faults_gdf = None

        # Folium objects
        self.map_object = None
        self.marker_group = None
        self.color_map = None

    def load_data(self):
        """Load events, legend, optionally compute distances, filter, build color map."""
        # 1) Load events
        try:
            self.events_df = pd.read_csv(self.events_csv)
            logger.info(f"Loaded {len(self.events_df)} events from '{self.events_csv}'.")
        except Exception as e:
            logger.error(f"Could not load {self.events_csv}: {e}")
            return

        # 2) Check for lat/lon vs. x_col/y_col
        has_latlon = ('latitude' in self.events_df.columns) and ('longitude' in self.events_df.columns)
        has_xy = (self.x_col is not None) and (self.y_col is not None)

        if not has_latlon and not has_xy:
            logger.error("Events must have either 'latitude'/'longitude' or x_col/y_col. Missing both.")
            return

        # 3) Convert XY -> lat/lon if needed
        if has_xy and not has_latlon:
            if self.x_col not in self.events_df.columns or self.y_col not in self.events_df.columns:
                logger.error(f"Missing columns '{self.x_col}' or '{self.y_col}' in events_csv.")
                return
            logger.info(f"Converting {self.x_col},{self.y_col} -> lat,lon from CRS '{self.location_crs}'.")
            lon, lat = convert_xy_to_latlon(
                self.events_df[self.x_col].values,
                self.events_df[self.y_col].values,
                source_crs=self.location_crs,
                target_crs='EPSG:4326'
            )
            self.events_df['longitude'] = lon
            self.events_df['latitude'] = lat

        self.events_df.dropna(subset=['latitude', 'longitude'], inplace=True)

        # 4) Check mandatory magnitude column
        if self.mandatory_mag_col not in self.events_df.columns:
            logger.error(f"Mandatory magnitude column '{self.mandatory_mag_col}' is missing.")
            return
        # Convert magnitude to numeric
        self.events_df[self.mandatory_mag_col] = pd.to_numeric(self.events_df[self.mandatory_mag_col], errors='coerce')
        self.events_df.dropna(subset=[self.mandatory_mag_col], inplace=True)

        # 5) Load legend
        try:
            self.legend_df = pd.read_csv(self.legend_csv)
            logger.info(f"Loaded legend from '{self.legend_csv}'. Fields: {list(self.legend_df['Field'])}")
        except Exception as e:
            logger.error(f"Could not load legend_csv: {e}")
            return

        # 6) Compute distances + filter if configured
        if self.calculate_distance:
            self._compute_distances()
            # Distance filter
            multiplier = self.event_config.event_radius_multiplier or 1.0
            event_radius_km = self.map_config.radius_km * multiplier
            logger.info(f"Filtering events within {event_radius_km} km of site.")
            before_count = len(self.events_df)
            self.events_df = self.events_df[self.events_df['Repi'] <= event_radius_km]
            logger.info(f"Distance filter dropped {before_count - len(self.events_df)} events. Remaining: {len(self.events_df)}")

        # Magnitude filter if vmin is set
        if self.event_config.vmin is not None:
            logger.info(f"Filtering out events below magnitude {self.event_config.vmin}.")
            before_count2 = len(self.events_df)
            self.events_df = self.events_df[self.events_df[self.mandatory_mag_col] >= self.event_config.vmin]
            logger.info(f"Magnitude filter dropped {before_count2 - len(self.events_df)} events. Remaining: {len(self.events_df)}")

        # 7) Build color map
        self._build_colormap()

        # 8) Load faults if included
        if self.fault_config and self.fault_config.include_faults:
            self._load_faults()

        # 9) Load stations if station file provided
        if self.station_config and self.station_config.station_file_path:
            self._load_stations()

    def _compute_distances(self):
        logger.info("Calculating distances vectorized (Haversine)...")
        calculate_distances_vectorized(
            events_df=self.events_df,
            center_lat=self.map_config.latitude,
            center_lon=self.map_config.longitude,
            lat_col='latitude',
            lon_col='longitude',
            out_col='Repi'
        )
        logger.info("Distances computed and stored in 'Repi' column.")

    def _build_colormap(self):
        """Set up a color scale from vmin/vmax or data range, based on magnitude."""
        if self.events_df.empty:
            logger.warning("No events left after filters; skipping color map.")
            return

        vmin = self.event_config.vmin
        vmax = self.event_config.vmax
        mag_values = self.events_df[self.mandatory_mag_col]
        data_min, data_max = mag_values.min(), mag_values.max()

        if vmin is None:
            vmin = math.floor(data_min * 2) / 2.0
        if vmax is None:
            vmax = math.ceil(data_max * 2) / 2.0

        logger.info(f"Building color map for {self.mandatory_mag_col} from {vmin} to {vmax}, reversed={self.event_config.color_reversed}.")
        colormap = plt.get_cmap(self.event_config.color_palette)
        if self.event_config.color_reversed:
            colormap = colormap.reversed()

        self.color_map = branca.colormap.LinearColormap(
            colors=[colormap(i / colormap.N) for i in range(colormap.N)],
            vmin=vmin,
            vmax=vmax
        )
        self.color_map.caption = self.event_config.legend_title or "Magnitude"
        logger.info("Color map built.")

    def _load_faults(self):
        logger.info(f"Loading faults from {self.fault_config.faults_gem_file_path}...")
        try:
            gdf = load_faults(self.fault_config.faults_gem_file_path, self.fault_config.coordinate_system)
        except Exception as e:
            logger.error(f"Failed to load faults: {e}")
            return
        if not gdf.is_valid.all():
            logger.warning("Some fault geometries are invalid; removing them.")
            gdf = gdf[gdf.is_valid]

        self.faults_gdf = gdf
        logger.info(f"Faults loaded. Found {len(gdf)} features.")

    def _load_stations(self):
        logger.info(f"Loading stations from {self.station_config.station_file_path}...")
        try:
            df = load_stations_csv(self.station_config.station_file_path, self.station_config.coordinate_system)
        except Exception as e:
            logger.error(f"Failed to load stations: {e}")
            return
        self.stations_df = df
        logger.info(f"Stations loaded. Found {len(self.stations_df)} stations.")

    def get_map(self):
        """Construct the Folium map, add markers, heatmap, epicentral circles, color legend, etc."""
        self._initialize_folium_map()

        # Create a FeatureGroup for events
        self.marker_group = folium.FeatureGroup(name='Events')

        # Add event markers, cluster, heatmap
        self._add_event_markers()
        self._add_marker_cluster_layer()
        self._add_heatmap_layer()

        # Add epicentral circles
        self.add_epicentral_distance_layer()

        # Add faults if we loaded them
        if self.faults_gdf is not None and not self.faults_gdf.empty:
            self._add_faults()

        # Add stations if we have them
        if self.stations_df is not None and not self.stations_df.empty:
            self._add_stations()

        # Add tile layers, layer control, site marker, color legend
        self._add_site_marker()
        self._add_tile_layers()
        self._add_layer_control()
        self._add_fullscreen_button()
        self._add_color_legend()

        # Lock the bounding box to site radius * multiplier
        self._fit_to_bounds()

        return self.map_object

    def _initialize_folium_map(self):
        logger.info("Initializing Folium map...")
        self.map_object = folium.Map(
            location=[self.map_config.latitude, self.map_config.longitude],
            zoom_start=self.map_config.base_zoom_level,
            min_zoom=self.map_config.min_zoom_level,
            max_zoom=self.map_config.max_zoom_level,
            control_scale=True
        )

    def add_epicentral_distance_layer(self):
        logger.info("Adding epicentral distance layer with tooltips and labels...")

        max_distance = self.map_config.radius_km
        num_circles = max(5, min(self.map_config.epicentral_circles, 25))
        interval = max_distance / num_circles

        epicentral_layer = folium.FeatureGroup(name=self.map_config.epicentral_circles_title, show=True)

        for i in range(1, num_circles + 1):
            dist_km = i * interval
            radius_m = dist_km * 1000

            folium.Circle(
                location=[self.map_config.latitude, self.map_config.longitude],
                radius=radius_m,
                color='green',
                fill=False,
                weight=1,
                opacity=0.5,
                tooltip=folium.Tooltip(f"{dist_km:.1f} km")
            ).add_to(epicentral_layer)

            label_location = geodesic(kilometers=dist_km).destination(
                (self.map_config.latitude, self.map_config.longitude), 0
            )
            folium.Marker(
                location=[label_location.latitude, label_location.longitude],
                icon=folium.DivIcon(
                    html=f"""
                        <div style="
                            font-size: 12px;
                            color: green;
                            text-align: center;
                            transform: translate(-50%, -50%);
                            white-space: nowrap;">
                            {dist_km:.1f}
                        </div>
                    """
                ),
            ).add_to(epicentral_layer)

        epicentral_layer.add_to(self.map_object)
        logger.info("Epicentral distance layer with tooltips and labels added.")

    def _add_event_markers(self):
        legend_map = {}
        for _, row in self.legend_df.iterrows():
            field = str(row['Field']).strip()
            label = str(row['Legend']).strip()
            legend_map[field] = label

        for _, row_data in self.events_df.iterrows():
            mag = row_data[self.mandatory_mag_col]
            color = 'blue'
            if self.color_map:
                color = self.color_map(mag)

            lines = []
            if self.mandatory_mag_col in legend_map:
                label_for_mag = legend_map[self.mandatory_mag_col]
                lines.append(f"<b>{html.escape(label_for_mag)}</b> {html.escape(str(mag))}")
            else:
                lines.append(f"<b>Magnitude:</b> {mag}")

            lat_label = legend_map.get('latitude', 'Latitude:')
            lon_label = legend_map.get('longitude', 'Longitude:')
            lines.append(f"<b>{html.escape(lat_label)}</b> {row_data['latitude']:.5f}")
            lines.append(f"<b>{html.escape(lon_label)}</b> {row_data['longitude']:.5f}")

            for field_name, field_label in legend_map.items():
                if field_name in (self.mandatory_mag_col, 'latitude', 'longitude'):
                    continue
                if field_name in row_data:
                    val_str = str(row_data[field_name]).strip()
                    if val_str.startswith("http://") or val_str.startswith("https://"):
                        link_html = f'<a href="{html.escape(val_str)}" target="_blank">{html.escape(val_str)}</a>'
                        lines.append(f"<b>{html.escape(field_label)}</b> {link_html}")
                    else:
                        lines.append(f"<b>{html.escape(field_label)}</b> {html.escape(val_str)}")

            tooltip_html = "<br>".join(lines)

            radius_val = 4
            if self.event_config.vmin is not None:
                radius_val += (mag - self.event_config.vmin) * self.event_config.scaling_factor

            folium.CircleMarker(
                location=[row_data['latitude'], row_data['longitude']],
                radius=radius_val,
                color=color,
                fill=True,
                fill_opacity=0.7,
                tooltip=folium.Tooltip(tooltip_html)
            ).add_to(self.marker_group)

        self.marker_group.add_to(self.map_object)

    def _add_marker_cluster_layer(self):
        if self.events_df.empty:
            logger.warning("No events to cluster.")
            return

        cluster = MarkerCluster(name='Marker Cluster', show=False)
        for _, row_data in self.events_df.iterrows():
            lat_ = row_data['latitude']
            lon_ = row_data['longitude']
            mag_ = row_data[self.mandatory_mag_col]
            tip = f"Mag: {mag_:.2f} | ({lat_:.3f}, {lon_:.3f})"
            folium.Marker(location=[lat_, lon_], tooltip=tip).add_to(cluster)
        cluster.add_to(self.map_object)

    def _add_heatmap_layer(self):
        if self.events_df.empty:
            logger.warning("No events for heatmap.")
            return

        data = []
        for _, row in self.events_df.iterrows():
            data.append((row['latitude'], row['longitude'], row[self.mandatory_mag_col]))

        if not data:
            return

        heat_layer = plugins.HeatMap(
            data=data,
            name='Heatmap',
            min_opacity=self.event_config.heatmap_min_opacity,
            max_zoom=self.map_config.max_zoom_level,
            radius=self.event_config.heatmap_radius,
            blur=self.event_config.heatmap_blur
        )
        fg = folium.FeatureGroup(name='Heatmap', show=False)
        fg.add_child(heat_layer)
        fg.add_to(self.map_object)

    def _add_site_marker(self):
        popup_html = f"""
        <b>Site Project:</b> {self.map_config.project_name}<br>
        <b>Client:</b> {self.map_config.client}
        """
        folium.Marker(
            location=[self.map_config.latitude, self.map_config.longitude],
            icon=folium.Icon(color='red', icon='star', prefix='fa'),
            tooltip=self.map_config.project_name,
            popup=folium.Popup(popup_html, max_width=300)
        ).add_to(self.map_object)

    def _add_tile_layers(self):
        for layer_name, cfg in TILE_LAYER_CONFIGS.items():
            if layer_name != self.map_config.default_tile_layer:
                folium.TileLayer(
                    tiles=cfg['tiles'],
                    name=layer_name,
                    attr=cfg['attr'],
                    control=True,
                    max_zoom=self.map_config.max_zoom_level,
                    min_zoom=self.map_config.min_zoom_level
                ).add_to(self.map_object)

        default_cfg = TILE_LAYER_CONFIGS[self.map_config.default_tile_layer]
        folium.TileLayer(
            tiles=default_cfg['tiles'],
            name=self.map_config.default_tile_layer,
            attr=default_cfg['attr'],
            control=True,
            max_zoom=self.map_config.max_zoom_level,
            min_zoom=self.map_config.min_zoom_level
        ).add_to(self.map_object)

    def _add_layer_control(self):
        folium.LayerControl().add_to(self.map_object)

    def _add_fullscreen_button(self):
        plugins.Fullscreen(
            position='topleft',
            title='Full Screen',
            title_cancel='Exit Full Screen',
            force_separate_button=True
        ).add_to(self.map_object)

    def _add_color_legend(self):
        if self.color_map is not None:
            self.color_map.position = self.event_config.legend_position.lower()
            self.color_map.add_to(self.map_object)
            logger.info("Color legend added to the map.")
        else:
            logger.info("No color map to add.")

    def _fit_to_bounds(self):
        """
        Zoom out to strictly show bounding box of (radius_km * event_radius_multiplier)
        around site center, ignoring events or stations outside that radius.
        """
        logger.info("Fitting map strictly to site radius & multiplier...")

        lat_center = self.map_config.latitude
        lon_center = self.map_config.longitude
        multiplier = self.event_config.event_radius_multiplier or 1.0
        dist_km = self.map_config.radius_km * multiplier

        # Convert dist_km to lat/lon offsets (approx)
        lat_offset = dist_km / 111.0
        cos_lat = math.cos(math.radians(lat_center))
        if abs(cos_lat) < 1e-5:
            cos_lat = 1e-5
        lon_offset = dist_km / (111.0 * cos_lat)

        min_lat = lat_center - lat_offset
        max_lat = lat_center + lat_offset
        min_lon = lon_center - lon_offset
        max_lon = lon_center + lon_offset

        self.map_object.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]])
        logger.info(f"Strict bounding: lat=({min_lat}, {max_lat}), lon=({min_lon}, {max_lon}).")

    def _add_faults(self):
        logger.info("Adding fault lines to the map...")
        if self.faults_gdf is None or self.faults_gdf.empty:
            logger.warning("No fault lines to display.")
            return

        style_func = lambda x: {
            "color": self.fault_config.regional_faults_color,
            "weight": self.fault_config.regional_faults_weight,
            "opacity": 1.0
        }
        fault_layer = folium.GeoJson(
            data=self.faults_gdf,
            style_function=style_func,
            name='Faults',
            show=True
        )
        fault_layer.add_to(self.map_object)
        logger.info("Fault lines layer added.")

    def _add_stations(self):
        logger.info("Adding stations to the map...")
        if self.stations_df.empty:
            logger.warning("No station data to display.")
            return

        station_group = folium.FeatureGroup(name=self.station_config.layer_title, show=True)
        icon_map = {
            1: {'color': 'blue', 'icon': 'arrow-up', 'prefix': 'fa'},
            2: {'color': 'green', 'icon': 'arrows-h', 'prefix': 'fa'},
            3: {'color': 'red', 'icon': 'cube', 'prefix': 'fa'}
        }

        for _, row in self.stations_df.iterrows():
            lat_ = row['latitude']
            lon_ = row['longitude']
            num_axes = int(row.get('axes', 0))

            icon_conf = icon_map.get(num_axes, {
                'color': 'gray', 'icon': 'info-sign', 'prefix': 'fa'
            })
            tooltip_content = f"Station ID: {row.get('ID','?')}<br>Type: {row.get('type','N/A')}<br>Axes: {num_axes}"
            folium.Marker(
                location=[lat_, lon_],
                icon=folium.Icon(
                    color=icon_conf['color'],
                    icon=icon_conf['icon'],
                    prefix=icon_conf['prefix']
                ),
                tooltip=tooltip_content
            ).add_to(station_group)

        station_group.add_to(self.map_object)
        logger.info("Stations layer added.")