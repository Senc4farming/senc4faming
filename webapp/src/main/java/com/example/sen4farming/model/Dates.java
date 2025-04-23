package com.example.sen4farming.model;

import java.util.Date;


import com.example.sen4farming.util.DateOrderCheck;
import jakarta.validation.constraints.NotNull;

import org.springframework.format.annotation.DateTimeFormat;


@DateOrderCheck(startDateField = "startDate", endDateField = "endDate", message = "{end.date.before.start}")
public class Dates {
    private static final String AU_DATE_FORMAT = "dd/MM/yyyy";

    @NotNull(message = "{start.date.mandatory}")
    @DateTimeFormat(pattern = AU_DATE_FORMAT)
    private Date startDate;

    @NotNull(message = "{end.date.mandatory}")
    @DateTimeFormat(pattern = AU_DATE_FORMAT)
    private Date endDate;

    public Date getStartDate() {
        return startDate;
    }

    public void setStartDate(Date startDate) {
        this.startDate = startDate;
    }

    public Date getEndDate() {
        return endDate;
    }

    public void setEndDate(Date endDate) {
        this.endDate = endDate;
    }
}
