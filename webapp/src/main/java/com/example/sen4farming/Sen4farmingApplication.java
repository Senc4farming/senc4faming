package com.example.sen4farming;

import com.example.sen4farming.config.ConfiguationProperties;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration;
import org.springframework.boot.context.properties.ConfigurationPropertiesScan;

@SpringBootApplication
@EnableConfigurationProperties(ConfiguationProperties.class)
@ConfigurationPropertiesScan("com.jma.prolecto_sin_cambios_yml.config")
public class Sen4farmingApplication {

	public static void main(String[] args) {
		SpringApplication.run(Sen4farmingApplication.class, args);
	}

}
