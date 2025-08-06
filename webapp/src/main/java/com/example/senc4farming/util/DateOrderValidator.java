package com.example.senc4farming.util;

import com.example.senc4farming.service.DatesService;
import jakarta.validation.ConstraintValidator;
import jakarta.validation.ConstraintValidatorContext;
import org.springframework.beans.BeanWrapperImpl;


import java.util.Date;

public class DateOrderValidator implements ConstraintValidator<DateOrderCheck, Object> {


    private final DatesService datesService;

    private String startDate;
    private String endDate;

    public DateOrderValidator(DatesService datesService) {
        this.datesService = datesService;
    }

    @Override
    public void initialize(DateOrderCheck constraint) {
        this.startDate = constraint.startDateField();
        this.endDate = constraint.endDateField();
    }

    @Override
    public boolean isValid(Object value, ConstraintValidatorContext context) {

        Date dStartDate = (Date) new BeanWrapperImpl(value).getPropertyValue(this.startDate);
        Date dEndDate = (Date) new BeanWrapperImpl(value).getPropertyValue(this.endDate);
        if (dStartDate == null || dEndDate == null) {
            return true; // Let the other validator handle this
        }
        long interval = datesService.calculateDateInterval(dStartDate, dEndDate);
        return (interval >= 0);
    }
}