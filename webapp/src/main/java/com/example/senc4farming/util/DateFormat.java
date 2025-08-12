package com.example.senc4farming.util;

import lombok.Getter;

import java.sql.Timestamp;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;

@Getter
public final class DateFormat {

    private DateFormat(){

    }

    private static final SimpleDateFormat dateFormat0= new SimpleDateFormat("yyyy-MM-dd");
    private static final SimpleDateFormat dateFormat1 = new SimpleDateFormat("dd/MM/yyyy");
    private static final SimpleDateFormat dateFormat2 = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");

    private static final SimpleDateFormat dateFormat3 = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSSSS'Z'");


    public static Date parseDate(String date) {
        try {
            return new Date(dateFormat0.parse(date).getTime());
        } catch (ParseException e) {
            throw new IllegalArgumentException(e);
        }
    }

    public static Date parseDate1(String date) {
        try {
            return new Date(dateFormat1.parse(date).getTime());
        } catch (ParseException e) {
            throw new IllegalArgumentException(e);
        }
    }

    public static Timestamp parseTimestamp(String timestamp) {
        try {
            return new Timestamp(dateFormat2.parse(timestamp).getTime());
        } catch (ParseException e) {
            throw new IllegalArgumentException(e);
        }
    }

    public static Date parseDateZulu(String date) {
        try {
            return new Date(dateFormat3.parse(date).getTime());
        } catch (ParseException e) {
            throw new IllegalArgumentException(e);
        }
    }

    public static String parseDateZuluStr(String date) {
        try {
            return dateFormat1.format(dateFormat3.parse(date).getTime());
        } catch (ParseException e) {
            throw new IllegalArgumentException(e);
        }
    }

}
