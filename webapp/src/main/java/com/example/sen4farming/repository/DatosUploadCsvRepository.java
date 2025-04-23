package com.example.sen4farming.repository;

import com.example.sen4farming.model.DatosLucas2018;
import com.example.sen4farming.model.DatosUploadCsv;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface DatosUploadCsvRepository extends JpaRepository<DatosUploadCsv, Long> {
    List<DatosUploadCsv> findBySearchidAndAndPath(Integer id , String str);

    List<DatosUploadCsv> findBySearchid(Integer id);

    DatosUploadCsv findBySearchidAndPointidAndBandAndPathLike(Integer id ,String pointid,  String band, String str);

}
