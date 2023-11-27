import React from "react";
import {MapContainer, Marker, Popup, TileLayer} from "react-leaflet";


const icon = L.icon({
    iconUrl: '/placeholder.png',
    iconSize: [38, 38]
});

const position = [51.505, -0.09]

export default function Maps() {
    return (
        <MapContainer
            center={position}
            zoom = {13}
            style = {{width: "100%", height: "100%"}}
        >
            <TileLayer
                attribution = '&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors'
                url = ""
            />
            <Marker position={position} icon={icon}>
                <Popup>
                    A pretty CSS3 popup. <br/> Easily customizable.
                </Popup>
            </Marker>
        </MapContainer>
    );
}