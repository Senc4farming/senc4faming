package com.example.senc4farming.config.authentication;

import java.util.Collections;
import java.util.HashSet;
import java.util.Set;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;

@Service
public class AuthenticatedUsersService {
    private Set<String> authenticatedUsers = Collections.synchronizedSet(new HashSet<>());

    public void addAuthenticatedUser() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication != null && authentication.isAuthenticated()) {
            authenticatedUsers.add(authentication.getName());
        }
    }

    public void removeAuthenticatedUser() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication != null && authentication.isAuthenticated()) {
            authenticatedUsers.remove(authentication.getName());
        }
    }

    public Set<String> getAuthenticatedUsers() {
        return new HashSet<>(authenticatedUsers);  // Return a snapshot of the set
    }
}