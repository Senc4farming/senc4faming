package com.example.senc4farming.config;

import lombok.Getter;
import lombok.RequiredArgsConstructor;
import lombok.Setter;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.env.Environment;

@Configuration
@ConfigurationProperties(prefix = "general")
@Getter
@Setter
@RequiredArgsConstructor
public class ConfiguationProperties {
    private  Environment env;



    /**
     * IP of foo service used to blah.
     */
    private String ippythonserver = env.getProperty("python.api.ip");
    private Integer numberOfGeeImages = 80;
    private String offset = "0.01";
    private String kalmandistr = "101";



    // getter & setter
}