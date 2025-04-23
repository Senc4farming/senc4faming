package com.example.sen4farming.apiitem;


import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
public class AIModels {
    private Integer key;
    private String referencia;
    private String elemento;
    private String rmse;
    private String mae;
    private String r2;
    private String pearson;
    private String url;
}
