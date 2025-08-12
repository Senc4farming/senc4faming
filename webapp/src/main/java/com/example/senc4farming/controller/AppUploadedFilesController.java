package com.example.senc4farming.controller;

import com.example.senc4farming.config.ConfiguationProperties;
import com.example.senc4farming.config.details.SuperCustomerUserDetails;
import com.example.senc4farming.dto.FiltroConsultaKalmanDto;
import com.example.senc4farming.dto.UploadedFilesContentDto;
import com.example.senc4farming.dto.UploadedFilesDto;
import com.example.senc4farming.model.Dates;
import com.example.senc4farming.service.*;
import com.example.senc4farming.util.Constants;
import jakarta.validation.Valid;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;
import org.springframework.ui.ModelMap;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Optional;

import static com.example.senc4farming.util.DateFormat.parseDate1;

@Controller
public class AppUploadedFilesController extends AbstractController <UploadedFilesDto> {

    private final UploadedFilesService service;
    private final DatesService datesService;
    private final ConfiguationProperties configuationProperties;
    private final FiltroConsultaKalmanService filtroConsultaKalmanService;


    private static final String STR_LISTA = "lista";
    private static final String STR_VISOR = "visor/imagesuploaded";
    private static final String STR_UPLOAD_NO_ENC = "upload/detallesnoencontrado";
    private static final String STR_PATH_SENC4FARMING_API =  "/solovmwarewalgreen/projecto/SEN4CFARMING/api";
    public static String  roundDoubleValue(double value, int places) {
        if (places < 0) throw new IllegalArgumentException();

        long factor = (long) Math.pow(10, places);
        value = value * factor;
        long tmp = Math.round(value);
        double db = (double) tmp / factor;
        return Double.toString(db);
    }


    public AppUploadedFilesController(MenuService menuService, UploadedFilesService service, DatesService datesService, ConfiguationProperties configuationProperties, FiltroConsultaKalmanService filtroConsultaKalmanService) {
        super(menuService);
        this.service = service;
        this.datesService = datesService;
        this.configuationProperties = configuationProperties;
        this.filtroConsultaKalmanService = filtroConsultaKalmanService;
    }

    @GetMapping("/uploadedfiles")
    public String vistaGrupos(@RequestParam("page") Optional<Integer> page,
                                @RequestParam("size") Optional<Integer> size,
                                    ModelMap interfazConPantalla){


        //tenemos que leer la lista de usuarios
        //Que elemento me la ofrece?
        //listaUsrTodos
        //Obetenemos el objeto Page del servicio
        Integer pagina = 0;
        if (page.isPresent()) {
            pagina = page.get() -1;
        }
        Integer maxelementos = 10;
        if (size.isPresent()) {
            maxelementos = size.get();
        }
        //Obtenemos los datos del usuario
        Integer userId = ((SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal()).getUserID();

        Page<UploadedFilesDto> dtoPage =
                this.service.buscarTodosPorUsuarioId(PageRequest.of(pagina,maxelementos),userId);
        interfazConPantalla.addAttribute(pageNumbersAttributeKey,dameNumPaginas(dtoPage));
        interfazConPantalla.addAttribute(STR_LISTA, dtoPage);
        return "upload/listauploadpagina";
    }

    @GetMapping("/uploadedfiles/view/{id}")
    public String vistaDatosGrupo(@PathVariable("id") Integer id, ModelMap interfazConPantalla) throws IOException {
        //Con el id tengo que buscar el registro a nivel de entidad
        Optional<UploadedFilesDto> optdto = this.service.encuentraPorId(id);
        //Genero el objeto que me premite consultar kalman en las dos opciones csv y lucas
        //Obtenemos los datos del usuario de la sesión
        SuperCustomerUserDetails superCustomerUserDetails = (SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal();

        //¿Debería comprobar si hay datos?
        if (optdto.isPresent()){
            logger.info("El tipo es:%s"  ,optdto.get().getType() );
            if (optdto.get().getType().equals("csv")){
                String pathPython = optdto.get().getPath();
                String pathWebapp = pathPython.replace("/app",STR_PATH_SENC4FARMING_API);
                //Como encontré datos, leo el csv solo las 100 primeras filas
                List<UploadedFilesContentDto> csvitemslist = new ArrayList<>();
                String splitBy = ";";
                LineNumberReader reader =
                        new LineNumberReader
                                (new InputStreamReader(new FileInputStream(pathWebapp +"/"+ optdto.get().getDescription()), StandardCharsets.UTF_8));

                try{
                    String line;
                    while (((line = reader.readLine()) != null) && reader.getLineNumber() <= 500) {
                        //If line is empty nothing is done
                        if ( line.length() > 5){
                            // split on comma(',')
                            String[] datosCsv = line.split(splitBy);
                            // create car object to store values
                            UploadedFilesContentDto dto = new UploadedFilesContentDto();
                            // add values from csv to car object
                            dto.setDepth(datosCsv[0]);
                            dto.setPointid(datosCsv[1]);
                            double soc = 0;
                            try{
                                soc = Double.parseDouble(datosCsv[2]);
                            }catch (Exception ex){
                                soc = 0;
                            }
                            dto.setSoc(roundDoubleValue(soc,2));
                            double lat = Double.parseDouble(datosCsv[3]);
                            dto.setLatitude(roundDoubleValue(lat,5));
                            double longi = Double.parseDouble(datosCsv[4]);
                            dto.setLongitude(roundDoubleValue(longi,5));
                            dto.setSurveydate(datosCsv[5]);
                            dto.setElev(datosCsv[6]);
                            dto.setDesc1(datosCsv[7]);
                            dto.setDesc2(datosCsv[8]);
                            dto.setDesc3(datosCsv[9]);
                            // adding car objects to a list
                            csvitemslist.add(dto);
                        }
                    }
                }finally{
                    reader.close();
                }
                //Asigno atributos para kalman y muestro
                FiltroConsultaKalmanDto dtofiltroConsultaKanlam = new FiltroConsultaKalmanDto();
                dtofiltroConsultaKanlam.setCsvid(optdto.get().getId());
                dtofiltroConsultaKanlam.setUserid(superCustomerUserDetails.getUserID());
                dtofiltroConsultaKanlam.setDirstr(configuationProperties.getKalmandistr());
                dtofiltroConsultaKanlam.setOrigin("csv");
                dtofiltroConsultaKanlam.setOffset(0.01);
                dtofiltroConsultaKanlam.setCloudCover(5);
                dtofiltroConsultaKanlam.setNumDaysSerie(60);
                dtofiltroConsultaKanlam.setNumberOfGeeImages(5);
                dtofiltroConsultaKanlam.setPath(optdto.get().getPath()+"/"+optdto.get().getDescription());
                logger.info("path");
                logger.info(optdto.get().getPath());
                FiltroConsultaKalmanDto filtroConsultaKalmanDto =   filtroConsultaKalmanService.guardar(dtofiltroConsultaKanlam);
                interfazConPantalla.addAttribute(STR_LISTA,csvitemslist);
                interfazConPantalla.addAttribute("filtro",filtroConsultaKalmanDto);
            }
            else {
                List<UploadedFilesContentDto> csvitemslist1 = new ArrayList<>();
                //Asigno atributos y muestro
                interfazConPantalla.addAttribute(STR_LISTA,csvitemslist1);
            }
            return "upload/view";
        } else{
            //Mostrar página usuario no existe
            return STR_UPLOAD_NO_ENC;
        }
    }

    @GetMapping("/uploadedfiles/map/{id}")
    public String mapDatosGrupo(@PathVariable("id") Integer id, ModelMap interfazConPantalla, Dates dates) throws IOException {
        //Con el id tengo que buscar el registro a nivel de entidad
        Optional<UploadedFilesDto> optdto = this.service.encuentraPorId(id);
        String kml2 = Constants.KML2;
        String kmlfinal = Constants.KML1;
        Double latitude = 42.29511966573258;
        Double longitude = -3.683528642004319;
        //¿Debería comprobar si hay datos?
        if (optdto.isPresent()) {
            UploadedFilesDto uploadedFilesDto = optdto.get();
            logger.info("El tipo es: %s" , optdto.get().getType());
            if (optdto.get().getType().equals("csv")) {
                String pathPython = optdto.get().getPath();
                String pathWebapp = pathPython.replace("/app", STR_PATH_SENC4FARMING_API);
                String splitBy = ";";
                LineNumberReader reader =
                        new LineNumberReader
                                (new InputStreamReader(new FileInputStream(pathWebapp + "/" + optdto.get().getDescription()), StandardCharsets.UTF_8));
                try{
                    String line;
                    Integer numLine = 0;
                    while (((line = reader.readLine()) != null) && reader.getLineNumber() <= 500) {
                        //If line is empty nothing is done
                        if ( line.length() > 5){
                            numLine += 1;
                            // split on comma(',')
                            String[] datosCsv = line.split(splitBy);
                            // create car object to store values
                            UploadedFilesContentDto dto = new UploadedFilesContentDto();
                            // add values from csv to car object
                            dto.setDepth(datosCsv[0]);
                            dto.setPointid(datosCsv[1]);
                            double soc = 0;
                            try{
                                soc = Double.parseDouble(datosCsv[2]);
                            }catch (Exception ex){
                                soc = 0;
                            }
                            dto.setSoc(roundDoubleValue(soc,2));
                            double lat = Double.parseDouble(datosCsv[3]);
                            latitude = lat;
                            dto.setLatitude(roundDoubleValue(lat,5));
                            double longi = Double.parseDouble(datosCsv[4]);
                            longitude = longi;
                            dto.setLongitude(roundDoubleValue(longi,5));
                            dto.setSurveydate(datosCsv[5]);
                            dto.setElev(datosCsv[6]);
                            dto.setDesc1(datosCsv[7]);
                            dto.setDesc2(datosCsv[8]);
                            dto.setDesc3(datosCsv[9]);
                            // creating kml content
                            String kmlPlacemark = "<Placemark id=\"" + numLine + "\">";
                            kmlPlacemark += """
                                    <name></name><styleUrl>#style-cropland</styleUrl>
                                    <Snippet maxLines="0">empty</Snippet>
                                    <description><![CDATA[<table cellpadding="1" cellspacing="1">
                                    """;
                            kmlPlacemark += "<tr><td>survey_date:</td><td>";
                            kmlPlacemark += dto.getSurveydate();
                            kmlPlacemark += "</td><td>SOC:</td><td>";
                            kmlPlacemark += dto.getSoc();
                            kmlPlacemark += "</td><td>lc0_desc:</td><td>";
                            kmlPlacemark += dto.getDesc1();
                            kmlPlacemark += "</td><td>lc1_desc:</td><td>";
                            kmlPlacemark += dto.getDesc2();
                            kmlPlacemark += "</td><td>lu1_desc:</td><td>";
                            kmlPlacemark += dto.getDesc3();
                            kmlPlacemark += "</td></tr></table>]]></description><Point><coordinates>";
                            kmlPlacemark += dto.getLongitude() + "," + dto.getLatitude()  +  ",0</coordinates></Point></Placemark>";
                            kmlfinal += kmlPlacemark;
                        }
                    }
                }finally{
                    reader.close();
                }
                kmlfinal += kml2;
                //Remove file if exists
                String pathKml = pathWebapp + "/kmlgen.kml";
                File kmlfile = new File(pathKml);
                if(kmlfile.exists()) {
                    Files.delete(kmlfile.toPath());
                }

                //Write string to file
                try (PrintWriter out = new PrintWriter(pathKml)) {
                    out.println(kmlfinal);
                }
                uploadedFilesDto.setDescription("kmlgen.kml");
                uploadedFilesDto.setLatitude(latitude);
                uploadedFilesDto.setLongitude(longitude);
                logger.info("uploadedFilesDto.setLongitude(longitude);");
                logger.info(longitude);
                interfazConPantalla.addAttribute("file", uploadedFilesDto);
                return STR_VISOR;
            } else {
                uploadedFilesDto.setLatitude(latitude);
                uploadedFilesDto.setLongitude(longitude);
                interfazConPantalla.addAttribute("file", uploadedFilesDto);
                return STR_VISOR;
            }
        } else {
            //Mostrar página usuario no existe
            return STR_UPLOAD_NO_ENC;
        }
    }


    @PostMapping("/uploadedfiles/map/{id}")
    public String mapDatosGrupoPost(@PathVariable("id") Integer id, ModelMap interfazConPantalla, @Valid Dates dates, BindingResult result) throws IOException {
        if (result.hasErrors()) {
            return String.format("redirect:/uploadedfiles/map/%s", id);
        }
        logger.info(dates.getStartDate());

        long interval = datesService.calculateDateInterval(dates.getStartDate(), dates.getEndDate());
        logger.info(interval);
        //Con el id tengo que buscar el registro a nivel de entidad
        Optional<UploadedFilesDto> optdto = this.service.encuentraPorId(id);
        String kml2 = Constants.KML2;
        String kmlfinal = Constants.KML1;
        Double latitude = 42.29511966573258;
        Double longitude = -3.683528642004319;
        //¿Debería comprobar si hay datos?
        if (optdto.isPresent()) {
            UploadedFilesDto uploadedFilesDto = optdto.get();
            logger.info("El tipo es: %s" , optdto.get().getType());
            if (optdto.get().getType().equals("csv")) {
                String pathPython = optdto.get().getPath();
                String pathWebapp = pathPython.replace("/app", STR_PATH_SENC4FARMING_API);
                String splitBy = ";";
                LineNumberReader reader =
                        new LineNumberReader
                                (new InputStreamReader(new FileInputStream(pathWebapp + "/" + optdto.get().getDescription()), StandardCharsets.UTF_8));
                try{
                    String line;
                    Integer numLine = 0;
                    while (((line = reader.readLine()) != null) && reader.getLineNumber() <= 500) {
                        //If line is empty nothing is done
                        if (line.contains("Depth")){
                            logger.info("cabecera");

                        }else if ( line.length() > 5){
                            numLine += 1;
                            // split on comma(',')
                            String[] datosCsv = line.split(splitBy);
                            // create car object to store values
                            UploadedFilesContentDto dto = new UploadedFilesContentDto();
                            // add values from csv to car object
                            dto.setDepth(datosCsv[0]);
                            dto.setPointid(datosCsv[1]);
                            double soc = 0;
                            try{
                                soc = Double.parseDouble(datosCsv[2]);
                            }catch (Exception ex){
                                soc = 0;
                            }
                            dto.setSoc(roundDoubleValue(soc,2));
                            double lat = Double.parseDouble(datosCsv[3]);
                            latitude = lat;
                            dto.setLatitude(roundDoubleValue(lat,5));
                            double longi = Double.parseDouble(datosCsv[4]);
                            longitude = longi;
                            dto.setLongitude(roundDoubleValue(longi,5));
                            dto.setSurveydate(datosCsv[5]);
                            dto.setElev(datosCsv[6]);
                            dto.setDesc1(datosCsv[7]);
                            dto.setDesc2(datosCsv[8]);
                            dto.setDesc3(datosCsv[9]);
                            //Comprobamos el día
                            Date surveydate =     parseDate1(dto.getSurveydate());
                            if ( surveydate.compareTo(dates.getStartDate()) > 0 && surveydate.compareTo(dates.getEndDate()) < 0 ){
                                logger.info("dentro");
                                logger.info(dto.getSurveydate());
                                logger.info(surveydate);
                                // creating kml content
                                String kmlPlacemark = "<Placemark id=\"" + numLine + "\">";
                                kmlPlacemark += """
                                    <name>P</name><styleUrl>#style-cropland</styleUrl><Snippet maxLines="0">
                                    empty</Snippet><description><![CDATA[<table cellpadding="1" cellspacing="1">
                                    """;
                                kmlPlacemark += "<tr><td>survey_date:</td><td>";
                                kmlPlacemark += dto.getSurveydate();
                                kmlPlacemark += "</td><td>SOC:</td><td>";
                                kmlPlacemark += dto.getSoc();
                                kmlPlacemark += "</td><td>lc0_desc:</td><td>";
                                kmlPlacemark += dto.getDesc1();
                                kmlPlacemark += "</td><td>lc1_desc:</td><td>";
                                kmlPlacemark += dto.getDesc2();
                                kmlPlacemark += "</td><td>lu1_desc:</td><td>";
                                kmlPlacemark += dto.getDesc3();
                                kmlPlacemark += "</td></tr></table>]]></description><Point><coordinates>";
                                kmlPlacemark += dto.getLongitude() + "," + dto.getLatitude()  +  ",0</coordinates></Point></Placemark>";
                                kmlfinal += kmlPlacemark;
                            }
                        }
                    }
                }finally{
                    reader.close();
                }
                kmlfinal += kml2;
                //Remove file if exists
                String pathKml = pathWebapp + "/kmlgen.kml";
                File kmlfile = new File(pathKml);
                if(kmlfile.exists()) {
                   Files.delete(kmlfile.toPath());
                }

                //Write string to file
                try (PrintWriter out = new PrintWriter(pathKml)) {
                    out.println(kmlfinal);
                }
                uploadedFilesDto.setDescription("kmlgen.kml");
                uploadedFilesDto.setLatitude(latitude);
                uploadedFilesDto.setLongitude(longitude);
                logger.info("uploadedFilesDto.setLongitude(longitude);");
                logger.info(longitude);
                interfazConPantalla.addAttribute("file", uploadedFilesDto);
                return STR_VISOR;
            } else {
                uploadedFilesDto.setLatitude(latitude);
                uploadedFilesDto.setLongitude(longitude);
                interfazConPantalla.addAttribute("file", uploadedFilesDto);
                return STR_VISOR;
            }
        } else {
            //Mostrar página usuario no existe
            return STR_UPLOAD_NO_ENC;
        }
    }


    @PostMapping("/uploadedfiles/{idusr}/delete")
    public String eliminarDatosGrupo(@PathVariable("idusr") Integer id){
        //Con el id tengo que buscar el registro a nivel de entidad
        Optional<UploadedFilesDto> grupoDto = this.service.encuentraPorId(id);
        //¿Debería comprobar si hay datos?
        if (grupoDto.isPresent()){
            this.service.eliminarPorId(id);
            //Mostrar listado de usuarios
            return "redirect:/upload";
        } else{
            //Mostrar página usuario no existe
            return STR_UPLOAD_NO_ENC;
        }
    }


    //Postmaping para guardar
    @PostMapping("/uploadedfiles/{idusr}")
    public String guardarEdicionDatosGrupo(@PathVariable("idusr") Integer id, UploadedFilesDto dtoEntrada)  {
        //Cuidado que la password no viene
        //Necesitamos copiar la información que llega menos la password
        //Con el id tengo que buscar el registro a nivel de entidad
        Optional<UploadedFilesDto> dtoControl = this.service.encuentraPorId(id);
        //¿Debería comprobar si hay datos?
        if (dtoControl.isPresent()){
            //LLamo al método del servicioi para guardar los datos
            dtoEntrada.setId(id);
            this.service.guardar(dtoEntrada);

            return String.format("redirect:/upload/%s", id);
        } else {
            //Mostrar página usuario no existe
            return "detallesnoencontrado";
        }
    }

}
