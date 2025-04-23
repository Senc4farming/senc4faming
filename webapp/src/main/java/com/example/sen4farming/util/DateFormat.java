package com.example.sen4farming.util;

import java.sql.Timestamp;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;

public final class DateFormat {

    static final SimpleDateFormat DATE_FORMAT = new SimpleDateFormat("yyyy-MM-dd");
    static final SimpleDateFormat DATE_FORMAT_1 = new SimpleDateFormat("dd/MM/yyyy");
    static final SimpleDateFormat DATE_TIME_FORMAT = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");

    static final SimpleDateFormat DATE_TIME_FORMAT_ZULU = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSSSS'Z'");


    public static Date parseDate(String date) {
        try {
            return new Date(DATE_FORMAT.parse(date).getTime());
        } catch (ParseException e) {
            throw new IllegalArgumentException(e);
        }
    }

    public static Date parseDate_1(String date) {
        try {
            return new Date(DATE_FORMAT_1.parse(date).getTime());
        } catch (ParseException e) {
            throw new IllegalArgumentException(e);
        }
    }

    public static Timestamp parseTimestamp(String timestamp) {
        try {
            return new Timestamp(DATE_TIME_FORMAT.parse(timestamp).getTime());
        } catch (ParseException e) {
            throw new IllegalArgumentException(e);
        }
    }

    public static Date parseDateZulu(String date) {
        try {
            return new Date(DATE_TIME_FORMAT_ZULU.parse(date).getTime());
        } catch (ParseException e) {
            throw new IllegalArgumentException(e);
        }
    }

    public static String parseDateZuluStr(String date) {
        try {
            return new String(DATE_FORMAT_1.format(DATE_TIME_FORMAT_ZULU.parse(date).getTime()));
        } catch (ParseException e) {
            throw new IllegalArgumentException(e);
        }
    }

}
