package com.example.senc4farming.controller;


import com.example.senc4farming.dto.UploadFilesDto;
import com.example.senc4farming.service.MenuService;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

//@SessionAttributes("productos")
@Controller
public class AppUserGuide  extends AbstractController <UploadFilesDto> {

    private static final String STR_RUTAMENU =  "rutamenu";
    private static final String STR_URL_MENUAYUDA = "urlmenuayuda";

    public AppUserGuide(MenuService menuService) {
        super(menuService);
    }

    @GetMapping("/userguide/ctr/home")
    public String userguideCtrHome(HttpServletRequest request, Model model ) {

        model.addAttribute(STR_RUTAMENU,this.rutanavegacion(request));
        model.addAttribute(STR_URL_MENUAYUDA,this.urlmenuayuda(request));
        return "userguide/home";
    }

    @GetMapping("/userguide/ctr/ctr/users/login")
    public String userguideCtrCtrUsersLogin(HttpServletRequest request, Model model ) {

        model.addAttribute(STR_RUTAMENU,this.rutanavegacion(request));
        model.addAttribute(STR_URL_MENUAYUDA,this.urlmenuayuda(request));
        return "userguide/users/login";
    }

    @GetMapping("/userguide/ctr/users/userslisthelp")
    public String userguideCtrUsersUserslisthelp(HttpServletRequest request, Model model ) {

        model.addAttribute(STR_RUTAMENU,this.rutanavegacion(request));
        model.addAttribute(STR_URL_MENUAYUDA,this.urlmenuayuda(request));
        return "userguide/users/userslisthelp";
    }
    @GetMapping("/userguide/ctr/users/changepassw")
    public String userguideCtrUsersChangepassword(HttpServletRequest request, Model model ) {

        model.addAttribute(STR_RUTAMENU,this.rutanavegacion(request));
        model.addAttribute(STR_URL_MENUAYUDA,this.urlmenuayuda(request));
        return "userguide/users/changepassw";
    }
    @GetMapping("/userguide/ctr/users/userregistry")
    public String userguideCtrUsersUserregistry(HttpServletRequest request, Model model ) {

        model.addAttribute(STR_RUTAMENU,this.rutanavegacion(request));
        model.addAttribute(STR_URL_MENUAYUDA,this.urlmenuayuda(request));
        return "userguide/users/userregistry";
    }

    @GetMapping("/userguide/ctr/users/groups/groupslist")
    public String userguideCtrUsersGroupsGroupslist(HttpServletRequest request, Model model ) {

        model.addAttribute(STR_RUTAMENU,this.rutanavegacion(request));
        model.addAttribute(STR_URL_MENUAYUDA,this.urlmenuayuda(request));
        return "userguide/users/groups/groupslist";
    }
    @GetMapping("/userguide/ctr/users/groups/groupsregister")
    public String userguideCtrUsersGroupsGroupsregister(HttpServletRequest request, Model model ) {

        model.addAttribute(STR_RUTAMENU,this.rutanavegacion(request));
        model.addAttribute(STR_URL_MENUAYUDA,this.urlmenuayuda(request));
        return "userguide/users/groups/groupsregister";
    }

    @GetMapping("/userguide/ctr/users/resetpassword")
    public String userguideCtrUsersRestetpassword(HttpServletRequest request, Model model ) {

        model.addAttribute(STR_RUTAMENU,this.rutanavegacion(request));
        model.addAttribute(STR_URL_MENUAYUDA,this.urlmenuayuda(request));
        return "userguide/users/resetpassword";
    }

    @GetMapping("/userguide/ctr/copsh/listqueries")
    public String userguideCtrCopshListqueries(HttpServletRequest request, Model model ) {

        model.addAttribute(STR_RUTAMENU,this.rutanavegacion(request));
        model.addAttribute(STR_URL_MENUAYUDA,this.urlmenuayuda(request));
        return "userguide/copsh/listqueries";
    }
    @GetMapping("/userguide/ctr/copsh/newquery")
    public String userguideCtrCopshNewquery(HttpServletRequest request, Model model ) {

        model.addAttribute(STR_RUTAMENU,this.rutanavegacion(request));
        model.addAttribute(STR_URL_MENUAYUDA,this.urlmenuayuda(request));
        return "userguide/copsh/newquery";
    }
    @GetMapping("/userguide/ctr/copsh/evalsclist")
    public String userguideCtrCopshEvalsclist(HttpServletRequest request, Model model ) {

        model.addAttribute(STR_RUTAMENU,this.rutanavegacion(request));
        model.addAttribute(STR_URL_MENUAYUDA,this.urlmenuayuda(request));
        return "userguide/copsh/evalsclist";
    }
    @GetMapping("/userguide/ctr/copsh/evalscregistry")
    public String userguideCtrCopshEvalscregistry(HttpServletRequest request, Model model ) {

        model.addAttribute(STR_RUTAMENU,this.rutanavegacion(request));
        model.addAttribute(STR_URL_MENUAYUDA,this.urlmenuayuda(request));
        return "userguide/copsh/evalscregistry";
    }
    @GetMapping("/userguide/ctr/copsh/credentials")
    public String userguideCtrCopshCredentials(HttpServletRequest request, Model model ) {

        model.addAttribute(STR_RUTAMENU,this.rutanavegacion(request));
        model.addAttribute(STR_URL_MENUAYUDA,this.urlmenuayuda(request));
        return "userguide/copsh/credentials";
    }
    @GetMapping("/userguide/ctr/copsh/index")
    public String userguideCtrCopshIndex(HttpServletRequest request, Model model ) {

        model.addAttribute(STR_RUTAMENU,this.rutanavegacion(request));
        model.addAttribute(STR_URL_MENUAYUDA,this.urlmenuayuda(request));
        return "userguide/copsh/index";
    }

    @GetMapping("/userguide/ctr/csv/lucas2018")
    public String userguideCtrCsvLucas2018(HttpServletRequest request, Model model ) {

        model.addAttribute(STR_RUTAMENU,this.rutanavegacion(request));
        model.addAttribute(STR_URL_MENUAYUDA,this.urlmenuayuda(request));
        return "userguide/csv/lucas2018";
    }
    @GetMapping("/userguide/ctr/csv/listcsv")
    public String userguideCtrCsvListcsv(HttpServletRequest request, Model model ) {

        model.addAttribute(STR_RUTAMENU,this.rutanavegacion(request));
        model.addAttribute(STR_URL_MENUAYUDA,this.urlmenuayuda(request));
        return "userguide/csv/listcsv";
    }
    @GetMapping("/userguide/ctr/csv/uploadkml")
    public String userguideCtrCsvUploadkml(HttpServletRequest request, Model model ) {

        model.addAttribute(STR_RUTAMENU,this.rutanavegacion(request));
        model.addAttribute(STR_URL_MENUAYUDA,this.urlmenuayuda(request));
        return "userguide/csv/uploadkml";
    }
    @GetMapping("/userguide/ctr/csv/uploadcsv")
    public String userguideCtrCsvUploadcsv(HttpServletRequest request, Model model ) {

        model.addAttribute(STR_RUTAMENU,this.rutanavegacion(request));
        model.addAttribute(STR_URL_MENUAYUDA,this.urlmenuayuda(request));
        return "userguide/csv/uploadcsv";
    }
    @GetMapping("/userguide/ctr/csv/querysoc")
    public String userguideCtrCsvQuerysoc(HttpServletRequest request, Model model ) {

        model.addAttribute(STR_RUTAMENU,this.rutanavegacion(request));
        model.addAttribute(STR_URL_MENUAYUDA,this.urlmenuayuda(request));
        return "userguide/csv/querysoc";
    }
    @GetMapping("/userguide/ctr/csv/index")
    public String userguideCtrCsvIndex(HttpServletRequest request, Model model ) {

        model.addAttribute(STR_RUTAMENU,this.rutanavegacion(request));
        model.addAttribute(STR_URL_MENUAYUDA,this.urlmenuayuda(request));
        return "userguide/csv/index";
    }


    @GetMapping("/userguide/ctr/csv/gee/listcsv/getrefl")
    public String userguideCtrCsvGeeListcsvGetrefl(HttpServletRequest request, Model model ) {

        model.addAttribute(STR_RUTAMENU,this.rutanavegacion(request));
        model.addAttribute(STR_URL_MENUAYUDA,this.urlmenuayuda(request));
        return "userguide/csv/gee/getrefl";
    }
    @GetMapping("/userguide/ctr/csv/gee/listcsv/listrefl")
    public String userguideCtrCsvGeeListcsvListrefl(HttpServletRequest request, Model model ) {

        model.addAttribute(STR_RUTAMENU,this.rutanavegacion(request));
        model.addAttribute(STR_URL_MENUAYUDA,this.urlmenuayuda(request));
        return "userguide/csv/gee/listrefl";
    }
    @GetMapping("/userguide/ctr/csv/gee/listcsv/trainml")
    public String userguideCtrCsvGeeListcsvTrainml(HttpServletRequest request, Model model ) {

        model.addAttribute(STR_RUTAMENU,this.rutanavegacion(request));
        model.addAttribute(STR_URL_MENUAYUDA,this.urlmenuayuda(request));
        return "userguide/csv/gee/trainml";
    }
    @GetMapping("/userguide/ctr/csv/gee/listcsv/getsoc")
    public String userguideCtrCsvGeeListcsvGetsoc(HttpServletRequest request, Model model ) {

        model.addAttribute(STR_RUTAMENU,this.rutanavegacion(request));
        model.addAttribute(STR_URL_MENUAYUDA,this.urlmenuayuda(request));
        return "userguide/csv/gee/getsoc";
    }

    @GetMapping("/userguide/ctr/csv/copsh/listcsv/getrefl")
    public String userguideCtrCsvCopshListcsvGetrefl(HttpServletRequest request, Model model ) {

        model.addAttribute(STR_RUTAMENU,this.rutanavegacion(request));
        model.addAttribute(STR_URL_MENUAYUDA,this.urlmenuayuda(request));
        return "userguide/csv/copsh/getrefl";
    }
    @GetMapping("/userguide/ctr/csv/copsh/listcsv/listrefl")
    public String userguideCtrCsvCopshListcsvListrefl(HttpServletRequest request, Model model ) {

        model.addAttribute(STR_RUTAMENU,this.rutanavegacion(request));
        model.addAttribute(STR_URL_MENUAYUDA,this.urlmenuayuda(request));
        return "userguide/csv/copsh/listrefl";
    }
    @GetMapping("/userguide/ctr/csv/copsh/listcsv/trainml")
    public String userguideCtrCsvCopshListcsvTrainml(HttpServletRequest request, Model model ) {

        model.addAttribute(STR_RUTAMENU,this.rutanavegacion(request));
        model.addAttribute(STR_URL_MENUAYUDA,this.urlmenuayuda(request));
        return "userguide/csv/copsh/trainml";
    }
    @GetMapping("/userguide/ctr/csv/copsh/listcsv/getsoc")
    public String userguideCtrCsvCopshListcsvGetsoc(HttpServletRequest request, Model model ) {

        model.addAttribute(STR_RUTAMENU,this.rutanavegacion(request));
        model.addAttribute(STR_URL_MENUAYUDA,this.urlmenuayuda(request));
        return "userguide/csv/copsh/getsoc";
    }

    @GetMapping("/userguide/kalman")
    public String userguideKalmanList(HttpServletRequest request, Model model ) {

        model.addAttribute(STR_RUTAMENU,this.rutanavegacion(request));
        model.addAttribute(STR_URL_MENUAYUDA,this.urlmenuayuda(request));
        return "userguide/kalman/kalmanlist";
    }



}
