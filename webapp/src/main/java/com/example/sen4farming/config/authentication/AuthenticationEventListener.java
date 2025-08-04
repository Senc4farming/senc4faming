package com.example.sen4farming.config.authentication;

import org.springframework.context.event.EventListener;
import org.springframework.security.authentication.event.AuthenticationSuccessEvent;
import org.springframework.security.authentication.event.AuthenticationFailureBadCredentialsEvent;
import org.springframework.stereotype.Component;

@Component
public class AuthenticationEventListener {

    private final AuthenticatedUsersService authenticatedUsersService;

    public AuthenticationEventListener(AuthenticatedUsersService authenticatedUsersService) {
        this.authenticatedUsersService = authenticatedUsersService;
    }

    @EventListener
    public void onAuthenticationSuccess(AuthenticationSuccessEvent event) {
        String username = event.getAuthentication().getName();
        authenticatedUsersService.addAuthenticatedUser();
    }

    @EventListener
    public void onAuthenticationFailure(AuthenticationFailureBadCredentialsEvent event) {
        // Handle failed authentication (if needed)
    }
}