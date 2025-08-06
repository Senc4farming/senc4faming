package com.example.senc4farming.dto;

import com.example.senc4farming.model.SentinelQueryFiles;
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
