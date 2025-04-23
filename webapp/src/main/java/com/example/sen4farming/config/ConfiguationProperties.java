package com.example.sen4farming.config;

import lombok.Getter;
import lombok.Setter;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

@Configuration
@ConfigurationProperties(prefix = "general")
@Getter
@Setter
public class ConfiguationProperties {

    /**
     * IP of foo service used to blah.
     */
    private String ippythonserver = "192.168.200.128" ;
    private Integer numberOfGeeImages = 80;
    private String offset = "0.01";
    private String kalmandistr = "101";

    // getter & setter
}