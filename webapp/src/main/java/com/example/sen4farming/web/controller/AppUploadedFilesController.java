package com.example.sen4farming.web.controller;

import com.example.sen4farming.config.ConfiguationProperties;
import com.example.sen4farming.config.details.SuperCustomerUserDetails;
import com.example.sen4farming.dto.FiltroConsultaKalmanDto;
import com.example.sen4farming.dto.UploadedFilesContentDto;
import com.example.sen4farming.dto.UploadedFilesDto;
import com.example.sen4farming.model.Dates;
import com.example.sen4farming.service.*;
import com.example.sen4farming.util.Constants;
import jakarta.validation.Valid;
import jakarta.xml.bind.JAXBException;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;
import org.springframework.ui.ModelMap;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.*;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import java.io.*;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Optional;

import static com.example.sen4farming.util.DateFormat.parseDate_1;

@Controller
public class AppUploadedFilesController extends AbstractController <UploadedFilesDto> {

    private final UploadedFilesService service;
    private final UsuarioService usuarioService;
    private final DatesService datesService;
    private final ConfiguationProperties configuationProperties;
    private final FiltroConsultaKalmanService filtroConsultaKalmanService;
    public static String  roundDoubleValue(double value, int places) {
        if (places < 0) throw new IllegalArgumentException();

        long factor = (long) Math.pow(10, places);
        value = value * factor;
        long tmp = Math.round(value);
        double db = (double) tmp / factor;
        return Double.toString(db);
    }


    public AppUploadedFilesController(MenuService menuService, UploadedFilesService service, UsuarioService usuarioService, DatesService datesService, ConfiguationProperties configuationProperties, FiltroConsultaKalmanService filtroConsultaKalmanService) {
        super(menuService);
        this.service = service;
        this.usuarioService = usuarioService;
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
        //List<UsuarioDto>  lusrdto = this.service.listaUsrTodos();
        //interfazConPantalla.addAttribute("listausuarios", lusrdto);
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
        interfazConPantalla.addAttribute("lista", dtoPage);
        return "upload/listauploadpagina";
    }

    @GetMapping("/uploadedfiles/view/{id}")
    public String vistaDatosGrupo(@PathVariable("id") Integer id, ModelMap interfazConPantalla) throws IOException {
        //Con el id tengo que buscar el registro a nivel de entidad
        Optional<UploadedFilesDto> optdto = this.service.encuentraPorId(id);
        //Genero el objeto que me premite consultar kalman en las dos opciones csv y lucas
        //Obtenemos los datos del usuario de la sesión
        String userName = "no informado";
        SuperCustomerUserDetails superCustomerUserDetails = (SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal();

        //¿Debería comprobar si hay datos?
        if (optdto.isPresent()){
            System.out.println("El tipo es:" +optdto.get().getType() );
            if (optdto.get().getType().equals("csv")){
                String path_python = optdto.get().getPath();
                String path_webapp = path_python.replace("/app","/solovmwarewalgreen/projecto/SEN4CFARMING/api");
                //Como encontré datos, leo el csv solo las 100 primeras filas
                List<UploadedFilesContentDto> csvitemslist = new ArrayList<>();
                String splitBy = ";";
                LineNumberReader reader =
                        new LineNumberReader
                                (new InputStreamReader(new FileInputStream(path_webapp +"/"+ optdto.get().getDescription()), "UTF-8"));

                try{
                    String line;
                    while (((line = reader.readLine()) != null) && reader.getLineNumber() <= 500) {
                        //If line is empty nothing is done
                        //System.out.println(line);
                        if (line.contains("Depth")){
                            System.out.println("cabecera");

                        }else if ( line.length() > 5){
                            // split on comma(',')
                            //System.out.println(line);
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
                System.out.println("path");
                System.out.println(optdto.get().getPath());
                FiltroConsultaKalmanDto filtroConsultaKalmanDto =   filtroConsultaKalmanService.guardar(dtofiltroConsultaKanlam);
                interfazConPantalla.addAttribute("lista",csvitemslist);
                interfazConPantalla.addAttribute("filtro",filtroConsultaKalmanDto);
            }
            else {
                List<UploadedFilesContentDto> csvitemslist1 = new ArrayList<>();
                //Asigno atributos y muestro
                interfazConPantalla.addAttribute("lista",csvitemslist1);
            }
            return "upload/view";
        } else{
            //Mostrar página usuario no existe
            return "upload/detallesnoencontrado";
        }
    }

    @GetMapping("/uploadedfiles/map/{id}")
    public String mapDatosGrupo(@PathVariable("id") Integer id, ModelMap interfazConPantalla, Dates dates) throws IOException {
        //Con el id tengo que buscar el registro a nivel de entidad
        Optional<UploadedFilesDto> optdto = this.service.encuentraPorId(id);
        String kml2 = Constants.kml2;
        String kmlfinal = Constants.kml1;
        Double latitude = 42.29511966573258;
        Double longitude = -3.683528642004319;
        //¿Debería comprobar si hay datos?
        if (optdto.isPresent()) {
            UploadedFilesDto uploadedFilesDto = optdto.get();
            System.out.println("El tipo es:" + optdto.get().getType());
            if (optdto.get().getType().equals("csv")) {
                String path_python = optdto.get().getPath();
                String path_webapp = path_python.replace("/app", "/solovmwarewalgreen/projecto/SEN4CFARMING/api");
                List<UploadedFilesContentDto> csvitemslist = new ArrayList<>();
                String splitBy = ";";
                LineNumberReader reader =
                        new LineNumberReader
                                (new InputStreamReader(new FileInputStream(path_webapp + "/" + optdto.get().getDescription()), "UTF-8"));
                try{
                    String line;
                    Integer num_line = 0;
                    while (((line = reader.readLine()) != null) && reader.getLineNumber() <= 500) {
                        //If line is empty nothing is done
                        //System.out.println(line);
                        if (line.contains("Depth")){
                            System.out.println("cabecera");

                        }else if ( line.length() > 5){
                            num_line += 1;
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
                            String kml_placemark = "<Placemark id=\"" + num_line + "\">";
                            kml_placemark += """
                                    <name></name><styleUrl>#style-cropland</styleUrl>
                                    		<Snippet maxLines="0">empty</Snippet>
                                    		<description><![CDATA[<table cellpadding="1" cellspacing="1">
                                    """;
                            kml_placemark += "<tr><td>survey_date:</td><td>";
                            kml_placemark += dto.getSurveydate();
                            kml_placemark += "</td><td>SOC:</td><td>";
                            kml_placemark += dto.getSoc();
                            kml_placemark += "</td><td>lc0_desc:</td><td>";
                            kml_placemark += dto.getDesc1();
                            kml_placemark += "</td><td>lc1_desc:</td><td>";
                            kml_placemark += dto.getDesc2();
                            kml_placemark += "</td><td>lu1_desc:</td><td>";
                            kml_placemark += dto.getDesc3();
                            kml_placemark += "</td></tr></table>]]></description><Point><coordinates>";
                            kml_placemark += dto.getLongitude() + "," + dto.getLatitude()  +  ",0</coordinates></Point></Placemark>";
                            kmlfinal += kml_placemark;
                        }
                    }
                }finally{
                    reader.close();
                }
                kmlfinal += kml2;
                //Remove file if exists
                String path_kml = path_webapp + "/kmlgen.kml";
                File kmlfile = new File(path_kml);
                if(kmlfile.exists()) {
                    kmlfile.delete();
                }

                //Write string to file
                try (PrintWriter out = new PrintWriter(path_kml)) {
                    out.println(kmlfinal);
                }
                uploadedFilesDto.setDescription("kmlgen.kml");
                uploadedFilesDto.setLatitude(latitude);
                uploadedFilesDto.setLongitude(longitude);
                System.out.println("uploadedFilesDto.setLongitude(longitude);");
                System.out.println(longitude);
                interfazConPantalla.addAttribute("file", uploadedFilesDto);
                return "visor/imagesuploaded";
            } else {
                uploadedFilesDto.setLatitude(latitude);
                uploadedFilesDto.setLongitude(longitude);
                interfazConPantalla.addAttribute("file", uploadedFilesDto);
                return "visor/imagesuploaded";
            }
        } else {
            //Mostrar página usuario no existe
            return "upload/detallesnoencontrado";
        }
    }


    @PostMapping("/uploadedfiles/map/{id}")
    public String mapDatosGrupoPost(@PathVariable("id") Integer id, ModelMap interfazConPantalla, @Valid Dates dates, BindingResult result) throws IOException, JAXBException, ParserConfigurationException, SAXException {
        if (result.hasErrors()) {
            return String.format("redirect:/uploadedfiles/map/%s", id);
        }
        System.out.println(dates.getStartDate());

        long interval = datesService.calculateDateInterval(dates.getStartDate(), dates.getEndDate());
        System.out.println(interval);
        //Con el id tengo que buscar el registro a nivel de entidad
        Optional<UploadedFilesDto> optdto = this.service.encuentraPorId(id);
        String kml2 = Constants.kml2;
        String kmlfinal = Constants.kml1;
        Double latitude = 42.29511966573258;
        Double longitude = -3.683528642004319;
        //¿Debería comprobar si hay datos?
        if (optdto.isPresent()) {
            UploadedFilesDto uploadedFilesDto = optdto.get();
            System.out.println("El tipo es:" + optdto.get().getType());
            if (optdto.get().getType().equals("csv")) {
                String path_python = optdto.get().getPath();
                String path_webapp = path_python.replace("/app", "/solovmwarewalgreen/projecto/SEN4CFARMING/api");
                List<UploadedFilesContentDto> csvitemslist = new ArrayList<>();
                String splitBy = ";";
                LineNumberReader reader =
                        new LineNumberReader
                                (new InputStreamReader(new FileInputStream(path_webapp + "/" + optdto.get().getDescription()), "UTF-8"));
                try{
                    String line;
                    Integer num_line = 0;
                    while (((line = reader.readLine()) != null) && reader.getLineNumber() <= 500) {
                        //If line is empty nothing is done
                        //System.out.println(line);
                        if (line.contains("Depth")){
                            System.out.println("cabecera");

                        }else if ( line.length() > 5){
                            num_line += 1;
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
                            Date surveydate =     parseDate_1(dto.getSurveydate());
                            if ( surveydate.compareTo(dates.getStartDate()) > 0 && surveydate.compareTo(dates.getEndDate()) < 0 ){
                                System.out.println("dentro");
                                System.out.println(dto.getSurveydate());
                                System.out.println(surveydate);
                                // creating kml content
                                String kml_placemark = "<Placemark id=\"" + num_line + "\">";
                                kml_placemark += """
                                    <name>P</name><styleUrl>#style-cropland</styleUrl>
                                    		<Snippet maxLines="0">empty</Snippet>
                                    		<description><![CDATA[<table cellpadding="1" cellspacing="1">
                                    """;
                                kml_placemark += "<tr><td>survey_date:</td><td>";
                                kml_placemark += dto.getSurveydate();
                                kml_placemark += "</td><td>SOC:</td><td>";
                                kml_placemark += dto.getSoc();
                                kml_placemark += "</td><td>lc0_desc:</td><td>";
                                kml_placemark += dto.getDesc1();
                                kml_placemark += "</td><td>lc1_desc:</td><td>";
                                kml_placemark += dto.getDesc2();
                                kml_placemark += "</td><td>lu1_desc:</td><td>";
                                kml_placemark += dto.getDesc3();
                                kml_placemark += "</td></tr></table>]]></description><Point><coordinates>";
                                kml_placemark += dto.getLongitude() + "," + dto.getLatitude()  +  ",0</coordinates></Point></Placemark>";
                                kmlfinal += kml_placemark;

                            }


                        }
                    }
                }finally{
                    reader.close();
                }
                kmlfinal += kml2;
                //Remove file if exists
                String path_kml = path_webapp + "/kmlgen.kml";
                File kmlfile = new File(path_kml);
                if(kmlfile.exists()) {
                    kmlfile.delete();
                }

                //Write string to file
                try (PrintWriter out = new PrintWriter(path_kml)) {
                    out.println(kmlfinal);
                }
                uploadedFilesDto.setDescription("kmlgen.kml");
                uploadedFilesDto.setLatitude(latitude);
                uploadedFilesDto.setLongitude(longitude);
                System.out.println("uploadedFilesDto.setLongitude(longitude);");
                System.out.println(longitude);
                interfazConPantalla.addAttribute("file", uploadedFilesDto);
                return "visor/imagesuploaded";
            } else {
                String path_python1 = optdto.get().getPath();

                String path_webapp1 = path_python1.replace("/app/","/solovmwarewalgreen/projecto/SEN4CFARMING/api/");

                String file = path_webapp1 + "/" + optdto.get().getDescription();

                DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
                DocumentBuilder db = dbf.newDocumentBuilder();
                Document dom = db.parse(file);
                Element docEle = dom.getDocumentElement();
                NodeList nl = docEle.getChildNodes();
                int length = nl.getLength();
                System.out.println(length);
                for (int i = 0; i < length; i++) {
                    System.out.println(nl.item(i).getNodeType());
                    if (nl.item(i).getNodeType() == Node.ELEMENT_NODE) {
                        Element el = (Element) nl.item(i);
                        System.out.println(el.toString());

                    }
                }
                uploadedFilesDto.setLatitude(latitude);
                uploadedFilesDto.setLongitude(longitude);
                interfazConPantalla.addAttribute("file", uploadedFilesDto);
                return "visor/imagesuploaded";
            }
        } else {
            //Mostrar página usuario no existe
            return "upload/detallesnoencontrado";
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
            return "upload/detallesnoencontrado";
        }
    }


    //Postmaping para guardar
    @PostMapping("/uploadedfiles/{idusr}")
    public String guardarEdicionDatosGrupo(@PathVariable("idusr") Integer id, UploadedFilesDto dtoEntrada) throws Exception {
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
