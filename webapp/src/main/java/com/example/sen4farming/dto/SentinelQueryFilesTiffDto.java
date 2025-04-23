package com.example.sen4farming.dto;

import com.example.sen4farming.model.SentinelQueryFiles;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;


@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor

public class SentinelQueryFilesTiffDto {
    private Integer id;

    private String band;

    private String path;

    private SentinelQueryFiles sentinelQueryFilesfortiff;

}
