package com.example.sen4farming.web.controller;


import com.example.sen4farming.dto.UploadFilesDto;
import com.example.sen4farming.service.MenuService;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

//@SessionAttributes("productos")
@Controller
public class AppUserGuide  extends AbstractController <UploadFilesDto> {

    public AppUserGuide(MenuService menuService) {
        super(menuService);
    }

    @GetMapping("/userguide/ctr/home")
    public String userguide_ctr_home(HttpServletRequest request, Model model ) {

        model.addAttribute("rutamenu",this.rutanavegacion(request));
        model.addAttribute("urlmenuayuda",this.urlmenuayuda(request));
        return "userguide/home";
    }

    @GetMapping("/userguide/ctr/ctr/users/login")
    public String userguide_ctr_ctr_users_login(HttpServletRequest request, Model model ) {

        model.addAttribute("rutamenu",this.rutanavegacion(request));
        model.addAttribute("urlmenuayuda",this.urlmenuayuda(request));
        return "userguide/users/login";
    }

    @GetMapping("/userguide/ctr/users/userslisthelp")
    public String userguide_ctr_users_userslisthelp(HttpServletRequest request, Model model ) {

        model.addAttribute("rutamenu",this.rutanavegacion(request));
        model.addAttribute("urlmenuayuda",this.urlmenuayuda(request));
        return "userguide/users/userslisthelp";
    }
    @GetMapping("/userguide/ctr/users/changepassw")
    public String userguide_ctr_users_changepassword(HttpServletRequest request, Model model ) {

        model.addAttribute("rutamenu",this.rutanavegacion(request));
        model.addAttribute("urlmenuayuda",this.urlmenuayuda(request));
        return "userguide/users/changepassw";
    }
    @GetMapping("/userguide/ctr/users/userregistry")
    public String userguide_ctr_users_userregistry(HttpServletRequest request, Model model ) {

        model.addAttribute("rutamenu",this.rutanavegacion(request));
        model.addAttribute("urlmenuayuda",this.urlmenuayuda(request));
        return "userguide/users/userregistry";
    }

    @GetMapping("/userguide/ctr/users/groups/groupslist")
    public String userguide_ctr_users_groups_groupslist(HttpServletRequest request, Model model ) {

        model.addAttribute("rutamenu",this.rutanavegacion(request));
        model.addAttribute("urlmenuayuda",this.urlmenuayuda(request));
        return "userguide/users/groups/groupslist";
    }
    @GetMapping("/userguide/ctr/users/groups/groupsregister")
    public String userguide_ctr_users_groups_groupsregister(HttpServletRequest request, Model model ) {

        model.addAttribute("rutamenu",this.rutanavegacion(request));
        model.addAttribute("urlmenuayuda",this.urlmenuayuda(request));
        return "userguide/users/groups/groupsregister";
    }

    @GetMapping("/userguide/ctr/users/resetpassword")
    public String userguide_ctr_users_restetpassword(HttpServletRequest request, Model model ) {

        model.addAttribute("rutamenu",this.rutanavegacion(request));
        model.addAttribute("urlmenuayuda",this.urlmenuayuda(request));
        return "userguide/users/resetpassword";
    }

    @GetMapping("/userguide/ctr/copsh/listqueries")
    public String userguide_ctr_copsh_listqueries(HttpServletRequest request, Model model ) {

        model.addAttribute("rutamenu",this.rutanavegacion(request));
        model.addAttribute("urlmenuayuda",this.urlmenuayuda(request));
        return "userguide/copsh/listqueries";
    }
    @GetMapping("/userguide/ctr/copsh/newquery")
    public String userguide_ctr_copsh_newquery(HttpServletRequest request, Model model ) {

        model.addAttribute("rutamenu",this.rutanavegacion(request));
        model.addAttribute("urlmenuayuda",this.urlmenuayuda(request));
        return "userguide/copsh/newquery";
    }
    @GetMapping("/userguide/ctr/copsh/evalsclist")
    public String userguide_ctr_copsh_evalsclist(HttpServletRequest request, Model model ) {

        model.addAttribute("rutamenu",this.rutanavegacion(request));
        model.addAttribute("urlmenuayuda",this.urlmenuayuda(request));
        return "userguide/copsh/evalsclist";
    }
    @GetMapping("/userguide/ctr/copsh/evalscregistry")
    public String userguide_ctr_copsh_evalscregistry(HttpServletRequest request, Model model ) {

        model.addAttribute("rutamenu",this.rutanavegacion(request));
        model.addAttribute("urlmenuayuda",this.urlmenuayuda(request));
        return "userguide/copsh/evalscregistry";
    }
    @GetMapping("/userguide/ctr/copsh/credentials")
    public String userguide_ctr_copsh_credentials(HttpServletRequest request, Model model ) {

        model.addAttribute("rutamenu",this.rutanavegacion(request));
        model.addAttribute("urlmenuayuda",this.urlmenuayuda(request));
        return "userguide/copsh/credentials";
    }
    @GetMapping("/userguide/ctr/copsh/index")
    public String userguide_ctr_copsh_index(HttpServletRequest request, Model model ) {

        model.addAttribute("rutamenu",this.rutanavegacion(request));
        model.addAttribute("urlmenuayuda",this.urlmenuayuda(request));
        return "userguide/copsh/index";
    }

    @GetMapping("/userguide/ctr/csv/lucas2018")
    public String userguide_ctr_csv_lucas2018(HttpServletRequest request, Model model ) {

        model.addAttribute("rutamenu",this.rutanavegacion(request));
        model.addAttribute("urlmenuayuda",this.urlmenuayuda(request));
        return "userguide/csv/lucas2018";
    }
    @GetMapping("/userguide/ctr/csv/listcsv")
    public String userguide_ctr_csv_listcsv(HttpServletRequest request, Model model ) {

        model.addAttribute("rutamenu",this.rutanavegacion(request));
        model.addAttribute("urlmenuayuda",this.urlmenuayuda(request));
        return "userguide/csv/listcsv";
    }
    @GetMapping("/userguide/ctr/csv/uploadkml")
    public String userguide_ctr_csv_uploadkml(HttpServletRequest request, Model model ) {

        model.addAttribute("rutamenu",this.rutanavegacion(request));
        model.addAttribute("urlmenuayuda",this.urlmenuayuda(request));
        return "userguide/csv/uploadkml";
    }
    @GetMapping("/userguide/ctr/csv/uploadcsv")
    public String userguide_ctr_csv_uploadcsv(HttpServletRequest request, Model model ) {

        model.addAttribute("rutamenu",this.rutanavegacion(request));
        model.addAttribute("urlmenuayuda",this.urlmenuayuda(request));
        return "userguide/csv/uploadcsv";
    }
    @GetMapping("/userguide/ctr/csv/querysoc")
    public String userguide_ctr_csv_querysoc(HttpServletRequest request, Model model ) {

        model.addAttribute("rutamenu",this.rutanavegacion(request));
        model.addAttribute("urlmenuayuda",this.urlmenuayuda(request));
        return "userguide/csv/querysoc";
    }
    @GetMapping("/userguide/ctr/csv/index")
    public String userguide_ctr_csv_index(HttpServletRequest request, Model model ) {

        model.addAttribute("rutamenu",this.rutanavegacion(request));
        model.addAttribute("urlmenuayuda",this.urlmenuayuda(request));
        return "userguide/csv/index";
    }


    @GetMapping("/userguide/ctr/csv/gee/listcsv/getrefl")
    public String userguide_ctr_csv_gee_listcsv_getrefl(HttpServletRequest request, Model model ) {

        model.addAttribute("rutamenu",this.rutanavegacion(request));
        model.addAttribute("urlmenuayuda",this.urlmenuayuda(request));
        return "userguide/csv/gee/getrefl";
    }
    @GetMapping("/userguide/ctr/csv/gee/listcsv/listrefl")
    public String userguide_ctr_csv_gee_listcsv_listrefl(HttpServletRequest request, Model model ) {

        model.addAttribute("rutamenu",this.rutanavegacion(request));
        model.addAttribute("urlmenuayuda",this.urlmenuayuda(request));
        return "userguide/csv/gee/listrefl";
    }
    @GetMapping("/userguide/ctr/csv/gee/listcsv/trainml")
    public String userguide_ctr_csv_gee_listcsv_trainml(HttpServletRequest request, Model model ) {

        model.addAttribute("rutamenu",this.rutanavegacion(request));
        model.addAttribute("urlmenuayuda",this.urlmenuayuda(request));
        return "userguide/csv/gee/trainml";
    }
    @GetMapping("/userguide/ctr/csv/gee/listcsv/getsoc")
    public String userguide_ctr_csv_gee_listcsv_getsoc(HttpServletRequest request, Model model ) {

        model.addAttribute("rutamenu",this.rutanavegacion(request));
        model.addAttribute("urlmenuayuda",this.urlmenuayuda(request));
        return "userguide/csv/gee/getsoc";
    }

    @GetMapping("/userguide/ctr/csv/copsh/listcsv/getrefl")
    public String userguide_ctr_csv_copsh_listcsv_getrefl(HttpServletRequest request, Model model ) {

        model.addAttribute("rutamenu",this.rutanavegacion(request));
        model.addAttribute("urlmenuayuda",this.urlmenuayuda(request));
        return "userguide/csv/copsh/getrefl";
    }
    @GetMapping("/userguide/ctr/csv/copsh/listcsv/listrefl")
    public String userguide_ctr_csv_copsh_listcsv_listrefl(HttpServletRequest request, Model model ) {

        model.addAttribute("rutamenu",this.rutanavegacion(request));
        model.addAttribute("urlmenuayuda",this.urlmenuayuda(request));
        return "userguide/csv/copsh/listrefl";
    }
    @GetMapping("/userguide/ctr/csv/copsh/listcsv/trainml")
    public String userguide_ctr_csv_copsh_listcsv_trainml(HttpServletRequest request, Model model ) {

        model.addAttribute("rutamenu",this.rutanavegacion(request));
        model.addAttribute("urlmenuayuda",this.urlmenuayuda(request));
        return "userguide/csv/copsh/trainml";
    }
    @GetMapping("/userguide/ctr/csv/copsh/listcsv/getsoc")
    public String userguide_ctr_csv_copsh_listcsv_getsoc(HttpServletRequest request, Model model ) {

        model.addAttribute("rutamenu",this.rutanavegacion(request));
        model.addAttribute("urlmenuayuda",this.urlmenuayuda(request));
        return "userguide/csv/copsh/getsoc";
    }

    @GetMapping("/userguide/kalman")
    public String userguide_kalman_list(HttpServletRequest request, Model model ) {

        model.addAttribute("rutamenu",this.rutanavegacion(request));
        model.addAttribute("urlmenuayuda",this.urlmenuayuda(request));
        return "userguide/kalman/kalmanlist";
    }



}
