package com.example.sen4farming.dto;

import com.example.sen4farming.model.Usuario;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
public class UploadedFilesDto {
    private Integer id;
    private String path;
    private String description;

    private double latitude;
    private double longitude;
    private boolean shared = true;
    private String type;
    private Usuario usuarioUpload;

}
