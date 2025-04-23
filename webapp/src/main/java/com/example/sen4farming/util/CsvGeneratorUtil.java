package com.example.sen4farming.util;

import com.example.sen4farming.apiitem.DatosLucas2018Api;
import com.example.sen4farming.apiitem.DatosUploadCsvApi;
import com.example.sen4farming.apiitem.UploadedFilesReflectance;
import com.example.sen4farming.dto.DatosUploadCsvDto;
import org.springframework.stereotype.Component;

import java.util.List;

@Component
public class CsvGeneratorUtil {
    private static final String CSV_HEADER = "Longitude,Latitude,Id,Band,Reflectance,SOC\n";

    public String generateCsv(List<DatosLucas2018Api> lista) {
        StringBuilder csvContent = new StringBuilder();
        csvContent.append(CSV_HEADER);

        for (DatosLucas2018Api datosLucas2018Api : lista) {
            csvContent.append(datosLucas2018Api.getLongitud()).append(",")
                    .append(datosLucas2018Api.getLatitud()).append(",")
                    .append(datosLucas2018Api.getId()).append(",")
                    .append(datosLucas2018Api.getBand()).append(",")
                    .append(datosLucas2018Api.getReflectance()).append(",")
                    .append(datosLucas2018Api.getOc()).append("\n");
        }

        return csvContent.toString();
    }
    public String generateCsvdatosusr(List<UploadedFilesReflectance> lista) {
        StringBuilder csvContent = new StringBuilder();
        csvContent.append(CSV_HEADER);

        for (UploadedFilesReflectance uploadedFilesReflectance : lista) {
            csvContent.append(uploadedFilesReflectance.getLongitude()).append(",")
                    .append(uploadedFilesReflectance.getLatitude()).append(",")
                    .append(uploadedFilesReflectance.getId()).append(",")
                    .append(uploadedFilesReflectance.getBand()).append(",")
                    .append(uploadedFilesReflectance.getReflectance()).append(",")
                    .append(uploadedFilesReflectance.getSoc()).append("\n");
        }

        return csvContent.toString();
    }
    public String generateUploadedCsvdatos(List<DatosUploadCsvDto> lista) {
        StringBuilder csvContent = new StringBuilder();
        csvContent.append(CSV_HEADER);

        for (DatosUploadCsvDto itm : lista) {
            csvContent.append(itm.getLongitud()).append(",")
                    .append(itm.getLatitud()).append(",")
                    .append(itm.getId()).append(",")
                    .append(itm.getBand()).append(",")
                    .append(itm.getReflectance()).append(",")
                    .append(itm.getOc()).append("\n");
        }

        return csvContent.toString();
    }
}