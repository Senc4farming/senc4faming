package com.example.senc4farming;

import com.example.senc4farming.config.ConfiguationProperties;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.EnableConfigurationProperties;

@SpringBootApplication
@EnableConfigurationProperties(ConfiguationProperties.class)

public class Senc4farmingApplication {

	public static void main(String[] args) {
		SpringApplication.run(Senc4farmingApplication.class, args);
	}

}
