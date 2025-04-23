package com.example.sen4farming.util;

public class Constants {
    public static String
            GET = "GET",
            POST = "POST",
            DELETE = "DELETE",
            PUT = "PUT",
            PATCH = "PATCH";

    public static int STANDARD_TIMEOUT = 1000000;
    public static int STANDARD_TIMEOUT1 = 1000000;

    public static String kml1 = """
  <kml> 
  <Document>
    <name>P</name>
    <description>JMA Sen4Farming</description>
    <ScreenOverlay id="CopyrightNotice">
    <name>Copyright Notice</name>
      <description>
        Description
      </description>
    <Snippet>Copyright (c) OpenStreetMap Contributors. CC-BY-SA 2.0 License.</Snippet>
      <Icon>
        <href>OSMCopyright.png</href>
      </Icon>
      <overlayXY x="0" xunits="fraction" y="1" yunits="fraction"/>
      <screenXY x="0" xunits="fraction" y="1" yunits="fraction"/>
      <size x="0" xunits="fraction" y="0" yunits="fraction"/>
    </ScreenOverlay>
    <Folder>
      <name>POI</name>
    <description>SOC data points</description>
      <Folder>
        <name>1</name>
        <Style id="style-cropland">
          <IconStyle>
            <scale>0.2</scale>
            <Icon>
              <href>https://maps.google.com/mapfiles/kml/paddle/blu-circle.png</href>
            </Icon>
          </IconStyle>
        </Style>
		<Style id="style-other">
          <IconStyle>
            <scale>0.2</scale>
            <Icon>
              <href>https://maps.google.com/mapfiles/kml/paddle/blu-circle.png</href>
            </Icon>
          </IconStyle>
        </Style>""";
    public static String kml2 = "</Folder></Folder></Document></kml>";
}