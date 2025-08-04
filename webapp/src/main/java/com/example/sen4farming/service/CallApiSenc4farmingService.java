package com.example.sen4farming.service;

import lombok.Getter;
import org.springframework.stereotype.Service;
@Getter
@Service
public class CallApiSenc4farmingService {
    private final DatosUploadCsvService  datosUploadCsvService;
    private final DatosLucas2018Service datosLucas2018Service;
    private final FiltroListarArchivosService filtroListarArchivosService;
    private final SentinelQueryFilesService sentinelQueryFilesService;

    private final SentinelQueryFilesTiffService sentinelQueryFilesTiffService;
    private final EvalScriptService evalScriptService;
    private final EvalScriptLaunchService evalScriptLaunchService;
    private final FiltroConsultaKalmanService filtroConsultaKalmanService;

    public CallApiSenc4farmingService(DatosUploadCsvService datosUploadCsvService, DatosLucas2018Service datosLucas2018Service, FiltroListarArchivosService filtroListarArchivosService, SentinelQueryFilesService sentinelQueryFilesService, SentinelQueryFilesTiffService sentinelQueryFilesTiffService, EvalScriptService evalScriptService, EvalScriptLaunchService evalScriptLaunchService, FiltroConsultaKalmanService filtroConsultaKalmanService) {
        this.datosUploadCsvService = datosUploadCsvService;
        this.datosLucas2018Service = datosLucas2018Service;
        this.filtroListarArchivosService = filtroListarArchivosService;
        this.sentinelQueryFilesService = sentinelQueryFilesService;
        this.sentinelQueryFilesTiffService = sentinelQueryFilesTiffService;
        this.evalScriptService = evalScriptService;
        this.evalScriptLaunchService = evalScriptLaunchService;
        this.filtroConsultaKalmanService = filtroConsultaKalmanService;
    }
}
