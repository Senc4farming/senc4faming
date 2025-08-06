package com.example.senc4farming.controller;



import com.example.senc4farming.config.details.SuperCustomerUserDetails;
import com.example.senc4farming.dto.UploadFilesDto;
import com.example.senc4farming.model.UploadedFiles;
import com.example.senc4farming.service.MenuService;
import com.example.senc4farming.service.UploadedFilesService;
import com.example.senc4farming.service.UsuarioService;
import com.example.senc4farming.util.FileUploadUtil;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpSession;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;

import org.springframework.ui.Model;

import org.springframework.util.StringUtils;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.Files;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

//@SessionAttributes("productos")
@Controller
public class AppUploadController extends AbstractController <UploadFilesDto>  {
    private final UploadedFilesService service;

    private final UsuarioService usuarioService;

    public AppUploadController(MenuService menuService, UploadedFilesService service, UsuarioService usuarioService) {
        super(menuService);
        this.service = service;
        this.usuarioService = usuarioService;
    }


    @GetMapping("/upload")
    public String vistaGet(HttpServletRequest request, Model model ) throws IOException {
        //check content of user folder
        //Obtenemos los datos del usuario
        Integer userId = ((SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal()).getUserID();
        List<String> results = new ArrayList<String>();
        //Leemos desde el path de static la carpeta
        String uploadDirRel = "src_data_safe/userfiles/" + userId.toString() + "/csvcoords";
        //Usando path obtenemos la direccion url
        Path uploadDirRelPath = Paths.get(uploadDirRel);
        String uri = uploadDirRelPath.toUri().toString();
        logger.info("uri");
        logger.info(uri);
        //Buscamos la url con formato /<val>/<val>/<val>/<val>
        int lastIndex = uri.lastIndexOf(':');
        String uploadDir =uri.substring(lastIndex + 1, uri.length() ).replace("SEN4CFARMING/","SEN4CFARMING/api/files/");
        //check if user folder exists if not create
        logger.info(uploadDir);
        Files.createDirectories(Paths.get(uploadDir));
        File[] files = new File(uploadDir).listFiles();
        //If this pathname does not denote a directory, then listFiles() returns null.

        for (File file : files) {
            logger.info("leyendo uploaddir:" + uploadDir );
            logger.info(file.getName());
            if (file.isFile()) {
                results.add(file.getName());
            }
        }
        model.addAttribute("rutamenu",this.rutanavegacion(request));
        model.addAttribute("files",results);
        return "upload/upload";
    }



    @PostMapping("/upload")
    public String uploadPost(@RequestParam MultipartFile file, HttpSession session , HttpServletRequest request,Model model) throws IOException {
        String path=session.getServletContext().getRealPath("/");
        String filename=file.getOriginalFilename();

        String fileName = StringUtils.cleanPath(file.getOriginalFilename());
        //Obtenemos los datos del usuario
        Integer userId = ((SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal()).getUserID();
        String uploadDirApi = "/app/files/src_data_safe/userfiles/" + userId.toString() + "/csvcoords";
        //Leemos desde el path de static la carpeta
        String uploadDirRel = "src_data_safe/userfiles/" + userId.toString() + "/csvcoords";
        //Usando path obtenemos la direccion url
        Path uploadDirRelPath = Paths.get(uploadDirRel);
        String uri = uploadDirRelPath.toUri().toString();
        //Buscamos la url con formato /<val>/<val>/<val>/<val>
        int lastIndex = uri.lastIndexOf(':');
        String uploadDirreal =uri.substring(lastIndex + 1, uri.length() ).replace("SEN4CFARMING/","SEN4CFARMING/api/files/");

        //String uploadDirreal = "src_data_safe/userfiles/" + userId.toString() + "/csvcoords";
        if (FileUploadUtil.checkfile(uploadDirreal,fileName )){
            model.addAttribute("rutamenu",this.rutanavegacion(request));
            model.addAttribute("file",file);
            model.addAttribute("description","File alredy exists.");
        }
        else {
            //check if user folder exists if not create
            Files.createDirectories(Paths.get(uploadDirreal));

            FileUploadUtil.saveFile(uploadDirreal, fileName, file);
            //Insertamos en la tabla de csv
            UploadedFiles uploadedFiles = new UploadedFiles();
            uploadedFiles.setUsuarioUpload(usuarioService.buscar(userId).get());
            uploadedFiles.setPath(uploadDirApi);
            uploadedFiles.setDescription(fileName);
            uploadedFiles.setShared(false);
            uploadedFiles.setType("csv");
            UploadedFiles uploadedFilessaved = service.getRepo().save(uploadedFiles);
            model.addAttribute("rutamenu",this.rutanavegacion(request));
            model.addAttribute("file",file);
        }

        //return new ModelAndView("upload/fileUploadView","filename",path+"/"+filename);
        return "upload/fileUploadViewUno";
    }

    @GetMapping("/upload/kml")
    public String vistaGetKml(HttpServletRequest request,Model model ) throws IOException {
        //check content of user folder
        //Obtenemos los datos del usuario
        Integer userId = ((SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal()).getUserID();
        List<String> results = new ArrayList<String>();
        //Leemos desde el path de static la carpeta
        String uploadDirRel = "src_data_safe/appsharedfiles/kml/" + userId.toString() + "/files";
        //Usando path obtenemos la direccion url
        Path uploadDirRelPath = Paths.get(uploadDirRel);
        String uri = uploadDirRelPath.toUri().toString();
        //Buscamos la url con formato /<val>/<val>/<val>/<val>
        int lastIndex = uri.lastIndexOf(':');
        String uploadDir =uri.substring(lastIndex + 1, uri.length() ).replace("SEN4CFARMING/","SEN4CFARMING/api/files/");

        Files.createDirectories(Paths.get(uploadDir));
        File[] files = new File(uploadDir).listFiles();
        //If this pathname does not denote a directory, then listFiles() returns null.

        for (File file : files) {
            if (file.isFile()) {
                results.add(file.getName());
            }
        }
        model.addAttribute("rutamenu",this.rutanavegacion(request));
        model.addAttribute("files",results);
        return "upload/uploadkml";
    }




    @PostMapping("/upload/kml")
    public String uploadPostKML(@RequestParam MultipartFile file, HttpSession session , HttpServletRequest request,
                                Model model) throws IOException {
        String path=session.getServletContext().getRealPath("/");
        String filename=file.getOriginalFilename();

        String fileName = StringUtils.cleanPath(file.getOriginalFilename());
        //Obtenemos los datos del usuario
        Integer userId = ((SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal()).getUserID();
        String uploadDirApi = "/app/files/src_data_safe/appsharedfiles/kml/" + userId.toString() + "/files";
        //Leemos desde el path de static la carpeta
        String uploadDirRel = "src_data_safe/appsharedfiles/kml/" + userId.toString() + "/files";
        //Usando path obtenemos la direccion url
        Path uploadDirRelPath = Paths.get(uploadDirRel);
        String uri = uploadDirRelPath.toUri().toString();
        //Buscamos la url con formato /<val>/<val>/<val>/<val>
        int lastIndex = uri.lastIndexOf(':');
        String uploadDirreal =uri.substring(lastIndex + 1, uri.length() ).replace("SEN4CFARMING/","SEN4CFARMING/api/files/");

        if (FileUploadUtil.checkfile(uploadDirreal,fileName )){
            model.addAttribute("rutamenu",this.rutanavegacion(request));
            model.addAttribute("file",file);
            model.addAttribute("description","File alredy exists.");
        }
        else {
            //check if user folder exists if not create
            Files.createDirectories(Paths.get(uploadDirreal));

            FileUploadUtil.saveFile(uploadDirreal, fileName, file);
            //Insertamos en la tabla de csv
            UploadedFiles uploadedFiles = new UploadedFiles();
            uploadedFiles.setUsuarioUpload(usuarioService.buscar(userId).get());
            uploadedFiles.setPath(uploadDirApi);
            uploadedFiles.setDescription(fileName);
            uploadedFiles.setShared(false);
            uploadedFiles.setType("kml");
            UploadedFiles uploadedFilessaved = service.getRepo().save(uploadedFiles);
            model.addAttribute("rutamenu",this.rutanavegacion(request));
            model.addAttribute("file",file);
        }

        //return new ModelAndView("upload/fileUploadView","filename",path+"/"+filename);
        return "upload/fileUploadViewUno";
    }


    @GetMapping("/uploadimg")
    public String vistaGetImg( HttpServletRequest request, Model model){
        model.addAttribute("rutamenu",this.rutanavegacion(request));
        return "upload/uploadimg";
    }
    @PostMapping("/uploadimg")
    public String uploadImgPost(@RequestParam MultipartFile file, HttpSession session ,HttpServletRequest request,
                                Model model) throws IOException {
        String path=session.getServletContext().getRealPath("/");
        String filename=file.getOriginalFilename();

        String fileName = StringUtils.cleanPath(file.getOriginalFilename());


        String uploadDir = "src/main/resources/static/imagenes/";

        FileUploadUtil.saveFile(uploadDir, fileName, file);
        model.addAttribute("rutamenu",this.rutanavegacion(request));
        model.addAttribute("file",file);
        //return new ModelAndView("upload/fileUploadView","filename",path+"/"+filename);
        return "upload/fileUploadViewUno";
    }
}
