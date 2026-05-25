package com.smartlearn.config;

import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import javax.servlet.FilterChain;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

@Component
public class ApiKeyFilter extends OncePerRequestFilter {

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response,
                                    FilterChain chain) throws ServletException, IOException {
        String key = request.getHeader("X-Api-Key");
        if (key != null && !key.trim().isEmpty()) {
            ApiKeyHolder.set(key.trim());
        }
        try {
            chain.doFilter(request, response);
        } finally {
            ApiKeyHolder.clear();
        }
    }
}
