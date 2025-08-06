package com.example.senc4farming.util;

import com.example.senc4farming.config.details.SuperCustomerUserDetails;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.springframework.context.ApplicationListener;
import org.springframework.security.authentication.event.*;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;

    @Component
    public class LoginListener implements ApplicationListener<InteractiveAuthenticationSuccessEvent> {
        Logger logger = LogManager.getLogger(this.getClass());
        @Override
        public void onApplicationEvent(InteractiveAuthenticationSuccessEvent event)
        {
            //Comprobamos si hay usuario logeado
            if (SecurityContextHolder.getContext().getAuthentication().getPrincipal().equals("anonymousUser")){
                logger.info("%s: Usario no logeado" ,this.getClass());
            }
            else {
                logger.info( "%s: El usuario es: %s ", this.getClass(),
                        ((SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal()).getUsername());
            }
        }

    }
