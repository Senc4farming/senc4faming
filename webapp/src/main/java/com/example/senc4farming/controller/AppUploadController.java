package com.example.senc4farming.controller;



import com.example.senc4farming.config.details.SuperCustomerUserDetails;
import com.example.senc4farming.dto.UploadFilesDto;
import com.example.senc4farming.model.UploadedFiles;
import com.example.senc4farming.service.MenuService;
import com.example.senc4farming.service.UploadedFilesService;
import com.example.senc4farming.util.FileUploadUtil;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpSession;
import org.apache.commons.io.FilenameUtils;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;

import org.springframework.ui.Model;

import org.springframework.util.StringUtils;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.InputStream;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.Files;
import java.io.IOException;
import java.util.*;

//@SessionAttributes("productos")
@Controller
public class AppUploadController extends AbstractController <UploadFilesDto>  {
    private final UploadedFilesService service;


    private static final String STR_UPLOAD_VIEW_UNO  = "upload/fileUploadViewUno";
    private static final String STR_CSVCOORDS  ="/csvcoords";
    private static final String STR_RUTAMENU  ="rutamenu";
    private static final String STR_FILES  ="files";
    private static final String STR_FILES_B  ="/files";

    private static final String STR_SEN4CFARMING = "SEN4CFARMING/";
    private static final String STR_SEN4CFARMING_API = "SEN4CFARMING/api/files/";

    private static final String STR_DESCRIPTION = "description";

    public AppUploadController(MenuService menuService, UploadedFilesService service) {
        super(menuService);
        this.service = service;
    }


    @GetMapping("/upload")
    public String vistaGet(HttpServletRequest request, Model model ) throws IOException {
        //check content of user folder
        //Obtenemos los datos del usuario
        Integer userId = ((SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal()).getUserID();
        List<String> results = new ArrayList<>();
        //Leemos desde el path de static la carpeta
        String uploadDirRel = "src_data_safe/userfiles/" + userId.toString() + STR_CSVCOORDS;
        //Usando path obtenemos la direccion url
        Path uploadDirRelPath = Paths.get(uploadDirRel);
        String uri = uploadDirRelPath.toUri().toString();
        logger.info("uri");
        logger.info(uri);
        //Buscamos la url con formato /<val>/<val>/<val>/<val>
        int lastIndex = uri.lastIndexOf(':');
        String uploadDir =uri.substring(lastIndex + 1, uri.length() ).replace(STR_SEN4CFARMING,STR_SEN4CFARMING_API);
        //check if user folder exists if not create
        logger.info(uploadDir);
        Files.createDirectories(Paths.get(uploadDir));
        File[] files = new File(uploadDir).listFiles();
        //If this pathname does not denote a directory, then listFiles() returns null.

        for (File file : files) {
            logger.info("leyendo uploaddir: %s" , uploadDir );
            logger.info(file.getName());
            if (file.isFile()) {
                results.add(file.getName());
            }
        }
        model.addAttribute(STR_RUTAMENU,this.rutanavegacion(request));
        model.addAttribute(STR_FILES,results);
        return "upload/upload";
    }

    @PostMapping("/upload")
    public String uploadPost(@RequestParam MultipartFile file,
                             HttpSession session,
                             HttpServletRequest request,
                             Model model) throws IOException {

        if (file.isEmpty()) {
            model.addAttribute(STR_DESCRIPTION ,"Cannot upload empty file.");
            return STR_UPLOAD_VIEW_UNO;
        }

        // Validar tipo MIME permitido
        Map<String, List<String>> ALLOWED_FILE_TYPES = Map.of(
                "csv", List.of("text/csv") // para shapefiles u otros datasets comprimidos
        );
        // Sanitizar nombre
        String fileName = StringUtils.cleanPath(file.getOriginalFilename());

        // Extraer extensión (en minúsculas)
        String extension = FilenameUtils.getExtension(fileName).toLowerCase(Locale.ROOT);

        // Validar que la extensión está permitida
        if (!ALLOWED_FILE_TYPES.containsKey(extension)) {
            throw new IOException("Tipo de archivo no permitido: " + extension);
        }
        // intento de path traversal
        if (fileName.contains("..")) {
            throw new IOException("Invalid path sequence in file name: " + fileName);
        }

        Integer userId = ((SuperCustomerUserDetails) SecurityContextHolder
                .getContext().getAuthentication().getPrincipal()).getUserID();

        Path uploadDirPath = Paths.get("/app/files/src_data_safe/userfiles", userId.toString(), STR_CSVCOORDS);
        Files.createDirectories(uploadDirPath);

        Path targetPath = uploadDirPath.resolve(fileName).normalize();

        if (Files.exists(targetPath)) {
            model.addAttribute(STR_RUTAMENU, this.rutanavegacion(request));
            model.addAttribute(STR_FILES, file);
            model.addAttribute(STR_DESCRIPTION ,"File already exists.");
        } else {
            try (InputStream inputStream = file.getInputStream()) {
                Files.copy(inputStream, targetPath);
            }

            UploadedFiles uploadedFiles = new UploadedFiles();
            uploadedFiles.setUsuarioUpload(((SuperCustomerUserDetails) SecurityContextHolder
                    .getContext().getAuthentication().getPrincipal()).getUsuario());
            uploadedFiles.setPath(uploadDirPath.toString());
            uploadedFiles.setDescription(fileName);
            uploadedFiles.setShared(false);
            uploadedFiles.setType("csv");
            service.getRepo().save(uploadedFiles);

            model.addAttribute(STR_RUTAMENU, this.rutanavegacion(request));
            model.addAttribute(STR_FILES, file);
            model.addAttribute(STR_DESCRIPTION, "File uploaded successfully.");
        }

        return STR_UPLOAD_VIEW_UNO;
    }


    @GetMapping("/upload/kml")
    public String vistaGetKml(HttpServletRequest request,Model model ) throws IOException {
        //check content of user folder
        //Obtenemos los datos del usuario
        Integer userId = ((SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal()).getUserID();
        List<String> results = new ArrayList<>();
        //Leemos desde el path de static la carpeta
        String uploadDirRel = "src_data_safe/appsharedfiles/kml/" + userId.toString() + STR_FILES_B;
        //Usando path obtenemos la direccion url
        Path uploadDirRelPath = Paths.get(uploadDirRel);
        String uri = uploadDirRelPath.toUri().toString();
        //Buscamos la url con formato /<val>/<val>/<val>/<val>
        int lastIndex = uri.lastIndexOf(':');
        String uploadDir =uri.substring(lastIndex + 1, uri.length() ).replace(STR_SEN4CFARMING,STR_SEN4CFARMING_API);

        Files.createDirectories(Paths.get(uploadDir));
        File[] files = new File(uploadDir).listFiles();
        //If this pathname does not denote a directory, then listFiles() returns null.

        for (File file : files) {
            if (file.isFile()) {
                results.add(file.getName());
            }
        }
        model.addAttribute(STR_RUTAMENU,this.rutanavegacion(request));
        model.addAttribute(STR_FILES,results);
        return "upload/uploadkml";
    }




    @PostMapping("/upload/kml")
    public String uploadPostKML(@RequestParam MultipartFile file, HttpSession session , HttpServletRequest request,
                                Model model) throws IOException {
        if (file.isEmpty()) {
            model.addAttribute(STR_DESCRIPTION ,"Cannot upload empty file.");
            return STR_UPLOAD_VIEW_UNO;
        }

        // Validar tipo MIME permitido
        Map<String, List<String>> ALLOWED_FILE_TYPES = Map.of(
                "kml", List.of("application/vnd.google-earth.kml+xml") // para shapefiles u otros datasets comprimidos
        );
        // Sanitizar nombre
        String fileName = StringUtils.cleanPath(file.getOriginalFilename());

        // Extraer extensión (en minúsculas)
        String extension = FilenameUtils.getExtension(fileName).toLowerCase(Locale.ROOT);

        // Validar que la extensión está permitida
        if (!ALLOWED_FILE_TYPES.containsKey(extension)) {
            throw new IOException("Tipo de archivo no permitido: " + extension);
        }
        // intento de path traversal
        if (fileName.contains("..")) {
            throw new IOException("Invalid path sequence in file name: " + fileName);
        }

        //Obtenemos los datos del usuario
        Integer userId = ((SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal()).getUserID();
        String uploadDirApi = "/app/files/src_data_safe/appsharedfiles/kml/" + userId.toString() +STR_FILES_B;
        //Leemos desde el path de static la carpeta
        String uploadDirRel = "src_data_safe/appsharedfiles/kml/" + userId.toString() + STR_FILES_B;
        //Usando path obtenemos la direccion url
        Path uploadDirRelPath = Paths.get(uploadDirRel);
        String uri = uploadDirRelPath.toUri().toString();
        //Buscamos la url con formato /<val>/<val>/<val>/<val>
        int lastIndex = uri.lastIndexOf(':');
        String uploadDirreal =uri.substring(lastIndex + 1, uri.length() ).replace(STR_SEN4CFARMING,STR_SEN4CFARMING_API);

        if (FileUploadUtil.checkfile(uploadDirreal,fileName )){
            model.addAttribute(STR_RUTAMENU,this.rutanavegacion(request));
            model.addAttribute(STR_FILES,file);
            model.addAttribute(STR_DESCRIPTION, "File alredy exists.");
        }
        else {
            //check if user folder exists if not create
            Files.createDirectories(Paths.get(uploadDirreal));

            FileUploadUtil.saveFile(uploadDirreal, fileName, file);
            //Insertamos en la tabla de csv
            UploadedFiles uploadedFiles = new UploadedFiles();
            uploadedFiles.setUsuarioUpload(((SuperCustomerUserDetails) SecurityContextHolder
                    .getContext().getAuthentication().getPrincipal()).getUsuario());
            uploadedFiles.setPath(uploadDirApi);
            uploadedFiles.setDescription(fileName);
            uploadedFiles.setShared(false);
            uploadedFiles.setType("kml");
            service.getRepo().save(uploadedFiles);
            model.addAttribute(STR_RUTAMENU,this.rutanavegacion(request));
            model.addAttribute(STR_FILES,file);
        }

        return STR_UPLOAD_VIEW_UNO;
    }


    @GetMapping("/uploadimg")
    public String vistaGetImg( HttpServletRequest request, Model model){
        model.addAttribute(STR_RUTAMENU,this.rutanavegacion(request));
        return "upload/uploadimg";
    }
    @PostMapping("/uploadimg")

    public String uploadImgPost(@RequestParam MultipartFile file, HttpSession session ,HttpServletRequest request,
                                Model model) throws IOException {

        if (file.isEmpty()) {
            model.addAttribute(STR_DESCRIPTION ,"Cannot upload empty file.");
            return STR_UPLOAD_VIEW_UNO;
        }

        // Sanitizar nombre
        String fileName = StringUtils.cleanPath(file.getOriginalFilename());

        // intento de path traversal
        if (fileName.contains("..")) {
            throw new IOException("Invalid path sequence in file name: " + fileName);
        }


        String uploadDir = "src/main/resources/static/imagenes/";

        FileUploadUtil.saveFile(uploadDir, fileName, file);
        model.addAttribute(STR_RUTAMENU,this.rutanavegacion(request));
        model.addAttribute(STR_FILES,file);
        return STR_UPLOAD_VIEW_UNO;
    }
}
