package com.example.senc4farming.service.mapper;


import com.example.senc4farming.dto.EvalScriptLaunchDto;
import com.example.senc4farming.model.EvalScriptLaunch;
import lombok.NoArgsConstructor;
import org.modelmapper.ModelMapper;
import org.springframework.stereotype.Service;

@NoArgsConstructor
@Service
public class EvalScriptLaunchMapper extends AbstractServiceMapper<EvalScriptLaunch, EvalScriptLaunchDto> {
    //Convertir de entidad a dtoç
    @Override
    public EvalScriptLaunchDto toDto(EvalScriptLaunch entidad){
        final EvalScriptLaunchDto dto = new EvalScriptLaunchDto();
        ModelMapper modelMapper = new ModelMapper();
        modelMapper.map(entidad,dto);
        return dto;
    }
    //Convertir de dto a entidad
    @Override
    public EvalScriptLaunch toEntity(EvalScriptLaunchDto dto){
        final EvalScriptLaunch entidad = new EvalScriptLaunch();
        ModelMapper modelMapper = new ModelMapper();
        modelMapper.map(dto,entidad);
        return entidad;
    }

}
