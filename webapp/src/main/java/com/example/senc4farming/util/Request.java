package com.example.senc4farming.util;


// Data streaming
import lombok.Getter;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.json.JSONObject;

import java.io.*;

// Networking and HTTP/HTTPS
import java.net.HttpURLConnection;
import java.net.URL;

// Charsets
import java.nio.charset.StandardCharsets;

// Utilities
import java.util.HashMap;
import java.util.Map;
import java.util.zip.GZIPInputStream;
import java.util.List;

// Constants
@Getter
public class Request {
    private String method;
    private String output;
    private String errormessage;
    private Map<String, List<String>> headers;

    private static final String STR_APP_JSON = "application/json";
    private static final String STR_ACCEPT= "Accept";
    private static final String STR_CONTENT_TYPE = "Content-Type";
    Logger logger = LogManager.getLogger(this.getClass());
    /**
     * Default constructor that always makes a GET request
     * @param url URL to make a GET request
     */
    public Request(String url) throws IOException {
        this.method = Constants.GET;

        HttpURLConnection urlConnection;

        try {
            urlConnection = (HttpURLConnection) new URL(url).openConnection();

            urlConnection.setRequestMethod(this.method);

            urlConnection.setConnectTimeout(Constants.STANDARDTIMEOUT);
            urlConnection.setReadTimeout(Constants.STANDARDTIMEOUT);

            boolean redirect = false;

            // normally, 3xx is redirect
            int status = urlConnection.getResponseCode();
            if (status != HttpURLConnection.HTTP_OK && (status == HttpURLConnection.HTTP_MOVED_TEMP
                        || status == HttpURLConnection.HTTP_MOVED_PERM
                        || status == HttpURLConnection.HTTP_SEE_OTHER
                        || status == 308))
                    redirect = true;

            logger.info("Response Code ... %s" , status);
            if (redirect) {

                // get redirect url from "location" header field
                String newUrl = urlConnection.getHeaderField("Location");

                // get the cookie if need, for login
                String cookies = urlConnection.getHeaderField("Set-Cookie");

                // open the new connnection again
                urlConnection = (HttpURLConnection) new URL(newUrl).openConnection();
                urlConnection.setRequestProperty("Cookie", cookies);
                urlConnection.setConnectTimeout(Constants.STANDARDTIMEOUT);
                urlConnection.setReadTimeout(Constants.STANDARDTIMEOUT);
            }
            this.output = read(urlConnection);
            this.headers = urlConnection.getHeaderFields();
        } catch (IOException e) {
            logger.error(e.getMessage());
            throw e;
        }
    }

    /**
     * Parameterized constructor for read-only and writable requests that also accepts headers
     * @param url URL to request
     * @param method Request method
     * @param data Data to write to the request
     * @param headers Headers for the request
     */
    public Request(String url, String method, String data, String[][] headers) throws IOException {
        this.method = method.toUpperCase();
        if (data == null) data = "{}";
        if (headers == null) {
            Request readOnly = new Request(url);
            this.output = readOnly.output;
        } else {
            HttpURLConnection urlConnection;

            if (this.method.equals(Constants.POST) || this.method.equals(Constants.DELETE)
                    || this.method.equals(Constants.PUT) || this.method.equals(Constants.PATCH)) {
                    try {
                        urlConnection = (HttpURLConnection) new URL(url).openConnection();

                        urlConnection.setRequestMethod(this.method);

                        urlConnection.setConnectTimeout(Constants.STANDARDTIMEOUT);
                        urlConnection.setReadTimeout(Constants.STANDARDTIMEOUT);

                        urlConnection.setDoOutput(true);

                        // Add the headers
                        setHeaders(urlConnection, headers);

                        try {
                            byte[] bytes = data.getBytes(StandardCharsets.UTF_8);
                            int length = bytes.length;
                            urlConnection.setFixedLengthStreamingMode(length);

                            OutputStream outputStream = urlConnection.getOutputStream();
                            outputStream.write(bytes, 0, length);
                            outputStream.flush();
                            outputStream.close();
                        } finally {
                            this.output = read(urlConnection);
                            urlConnection.getInputStream().close();
                        }
                        this.headers = urlConnection.getHeaderFields();
                    } catch (IOException e) {
                        logger.error(e.getMessage());
                        throw  e;
                    }
            } else {
                try {
                    urlConnection = (HttpURLConnection) new URL(url).openConnection();

                    urlConnection.setRequestMethod(this.method);

                    urlConnection.setConnectTimeout(Constants.STANDARDTIMEOUT);
                    urlConnection.setReadTimeout(Constants.STANDARDTIMEOUT);

                    // Adds headers
                    setHeaders(urlConnection, headers);

                    this.output = read(urlConnection);
                    this.headers = urlConnection.getHeaderFields();
                } catch (IOException e) {
                    logger.error(e.getMessage());
                    throw  e;
                }

            }
        }
    }

    /**
     * Parameterized constructor for read-only and writable requests
     * @param url URL to request
     * @param method Request method
     * @param data Data to write to the request
     */
    public Request(String url, String method, String data) throws IOException {
        this.method = method.toUpperCase();

        if (data == null) data = "{}";

        HttpURLConnection urlConnection;

        if (this.method.equals(Constants.POST) || this.method.equals(Constants.DELETE) || this.method.equals(Constants.PUT) || this.method.equals(Constants.PATCH)) {
            try {
                urlConnection = (HttpURLConnection) new URL(url).openConnection();

                urlConnection.setRequestMethod(this.method);

                urlConnection.setConnectTimeout(Constants.STANDARDTIMEOUT);
                urlConnection.setReadTimeout(Constants.STANDARDTIMEOUT);

                urlConnection.setDoOutput(true);

                try {
                    byte[] bytes = data.getBytes(StandardCharsets.UTF_8);
                    int length = bytes.length;
                    urlConnection.setFixedLengthStreamingMode(length);

                    OutputStream outputStream = urlConnection.getOutputStream();
                    outputStream.write(bytes, 0, length);
                    outputStream.flush();
                    outputStream.close();
                } finally {
                    this.output = read(urlConnection);
                    urlConnection.getInputStream().close();
                }

                this.headers = urlConnection.getHeaderFields();
            } catch (IOException e) {
                logger.error(e.getMessage());
                throw  e;
            }
        } else {
            Request readOnly = new Request(url);
            this.output = readOnly.output;
            this.headers = readOnly.headers;
        }
    }
    /**
     * Overloaded constructor for POST requests only
     * @param url URL to request
     * @param jsonobject
     */
    public Request(String url, JSONObject requestParam) throws IOException {
        this.method = Constants.POST;

        HttpURLConnection urlConnection;

        try {
            urlConnection = (HttpURLConnection) new URL(url).openConnection();
            urlConnection.setRequestMethod(this.method);

            urlConnection.setConnectTimeout(Constants.STANDARDTIMEOUT_1);
            urlConnection.setReadTimeout(Constants.STANDARDTIMEOUT_1);
            urlConnection.setRequestProperty(STR_CONTENT_TYPE, STR_APP_JSON);
            urlConnection.setRequestProperty(STR_ACCEPT, STR_APP_JSON);
            urlConnection.setDoOutput(true);

            logger.info("Request(String url, JSONObject requestParam) : %s :03 " , url );


            try {
                byte[] bytes = requestParam.toString().getBytes(StandardCharsets.UTF_8);
                int length = bytes.length;
                urlConnection.setFixedLengthStreamingMode(length);
                OutputStream os = urlConnection.getOutputStream();
                os.write(bytes, 0, bytes.length);
            } finally {
                if (urlConnection.getResponseCode() == 200){
                    this.output = read(urlConnection);
                    urlConnection.getInputStream().close();
                }
                else
                {
                    this.errormessage = "{\"errormessage \": \""+ urlConnection.getResponseMessage() + "\", \" errorcode\": " + urlConnection.getResponseCode() + "}";
                    this.output = "{\"errormessage  \": \""+ urlConnection.getResponseMessage() + "\", \"errorcode \": " + urlConnection.getResponseCode() + "}";
                }
            }

            this.headers = urlConnection.getHeaderFields();
        } catch (IOException e) {
            logger.error(e.getMessage());
            throw  e;
        }
    }
    /**
            * Overloaded constructor for POST requests only
     * @param url URL to request
     * @param jsonobject
     */
    public Request(String url, JSONObject requestParam, Float f) throws IOException {
        this.method = Constants.POST;

        HttpURLConnection urlConnection;
        logger.info(f);
        try {
            urlConnection = (HttpURLConnection) new URL(url).openConnection();
            urlConnection.setRequestMethod(this.method);

            urlConnection.setConnectTimeout(Constants.STANDARDTIMEOUT_1);
            urlConnection.setReadTimeout(Constants.STANDARDTIMEOUT_1);
            urlConnection.setRequestProperty(STR_CONTENT_TYPE, STR_APP_JSON);
            urlConnection.setRequestProperty(STR_ACCEPT, STR_APP_JSON);
            urlConnection.setDoOutput(true);

            logger.info("Request(String url, JSONObject requestParam) :  %s 02",  url );


            try {
                byte[] bytes = requestParam.toString().getBytes(StandardCharsets.UTF_8);
                int length = bytes.length;
                urlConnection.setFixedLengthStreamingMode(length);
                OutputStream os = urlConnection.getOutputStream();
                os.write(bytes, 0, bytes.length);
            } finally {

                if (urlConnection.getResponseCode() == 200){
                    this.output = read(urlConnection);
                    this.errormessage = "";
                    urlConnection.getInputStream().close();
                }
                else
                {
                    this.errormessage = "{\"errormessage\": \""+ urlConnection.getResponseMessage() + "\", \"errorcode\": " + urlConnection.getResponseCode() + "}";
                    this.output = readerror(urlConnection);
                }
            }
            logger.info("antes de this.headers  ");
            this.headers = urlConnection.getHeaderFields();
        } catch (IOException e) {
            logger.error(e.getMessage());
            throw  e;
        }
    }

    /**
     * Overloaded constructor for POST requests only
     * @param url URL to request
     * @param jsonobject
     * @param path on java server
     */
    public Request(String url, JSONObject requestParam, String path) throws IOException {
        this.method = Constants.POST;

        HttpURLConnection urlConnection;

        try {
            urlConnection = (HttpURLConnection) new URL(url).openConnection();
            urlConnection.setRequestMethod(this.method);

            urlConnection.setConnectTimeout(Constants.STANDARDTIMEOUT);
            urlConnection.setReadTimeout(Constants.STANDARDTIMEOUT);
            urlConnection.setRequestProperty(STR_CONTENT_TYPE, STR_APP_JSON);
            urlConnection.setRequestProperty(STR_ACCEPT, STR_APP_JSON);
            urlConnection.setDoOutput(true);

            logger.info("Request(String url, JSONObject requestParam , String action) : %s 01",url);

            // This will get input data from the server
            InputStream inputStream = null;

            // This will read the data from the server
            byte[] bytes = requestParam.toString().getBytes(StandardCharsets.UTF_8);
            int lengthJson = bytes.length;
            urlConnection.setFixedLengthStreamingMode(lengthJson);
            OutputStream os = urlConnection.getOutputStream();
            os.write(bytes, 0, bytes.length);

            // Requesting input data from server
            inputStream = urlConnection.getInputStream();
            try(OutputStream outputStream = new FileOutputStream(path)) {

                // Limiting byte written to file per loop
                byte[] bufferout = new byte[2048];

                // Increments file size
                int length;

                // Looping until server finishes
                while ((length = inputStream.read(bufferout)) != -1) {
                    // Writing data
                    outputStream.write(bufferout, 0, length);
                }
            } finally {
                this.output = read(urlConnection);
                urlConnection.getInputStream().close();
            }
            // closing used resources
            // The computer will not be able to use the image
            // This is a must

            inputStream.close();

            this.headers = urlConnection.getHeaderFields();
        } catch (IOException e) {
            logger.error(e.getMessage());
            throw  e;
        }
    }
    /**
     * Overloaded constructor for POST requests only
     * @param url URL to request
     * @param data Data to post
     */
    public Request(String url, String data) throws IOException {
        this.method = Constants.POST;

        HttpURLConnection urlConnection;

        try {
            urlConnection = (HttpURLConnection) new URL(url).openConnection();

            urlConnection.setRequestMethod(this.method);

            urlConnection.setConnectTimeout(Constants.STANDARDTIMEOUT);
            urlConnection.setReadTimeout(Constants.STANDARDTIMEOUT);

            urlConnection.setDoOutput(true);

            try {
                byte[] bytes = data.getBytes(StandardCharsets.UTF_8);
                int length = bytes.length;
                urlConnection.setFixedLengthStreamingMode(length);

                OutputStream outputStream = urlConnection.getOutputStream();
                outputStream.write(bytes, 0, length);
                outputStream.flush();
                outputStream.close();
            } finally {
                this.output = read(urlConnection);
                urlConnection.getInputStream().close();
            }

            this.headers = urlConnection.getHeaderFields();
        } catch (IOException e) {
            logger.error(e.getMessage());
            throw  e;
        }
    }
    /**
     * Method will read getErrorStream from HTTP/HTTPS requests
     * @param connection The connection as an instance of HttpURLConnection
     * @return Output as a String from reading the connection output
     */
    public  String readerror(HttpURLConnection connection) throws IOException {
        InputStream connectionInputStream = null;
        connectionInputStream = connection.getErrorStream();

        Reader reader = null;
        if (connection.getContentEncoding() != null) {
            try {
                assert connectionInputStream != null;
                reader = new InputStreamReader(new GZIPInputStream(connectionInputStream));
            } catch (IOException e) {
                logger.error(e.getMessage());
                throw  e;
            }
        } else {
            reader = new InputStreamReader(connection.getErrorStream());
        }

        // Empty char value
        int ch;

        // String Builder to add to the final string
        StringBuilder stringBuilder = new StringBuilder();

        // Appending the data to a String Builder
        while (true) {
            try {
                assert reader != null;
                ch = reader.read();
                if (ch == -1) {
                    return stringBuilder.toString();
                }

                stringBuilder.append((char) ch);
            } catch (IOException e) {
                logger.error(e.getMessage());
                throw  e;
            }
        }
    }

    /**
     * Method will read output from HTTP/HTTPS requests
     * @param connection The connection as an instance of HttpURLConnection
     * @return Output as a String from reading the connection output
     */
    public  String read(HttpURLConnection connection) throws IOException {
        InputStream connectionInputStream = null;
        try {
            connectionInputStream = connection.getInputStream();
        } catch (IOException e) {
            logger.error(e.getMessage());
            throw  e;
        }

        Reader reader = null;
        if (connection.getContentEncoding() != null) {
            try {
                assert connectionInputStream != null;
                reader = new InputStreamReader(new GZIPInputStream(connectionInputStream));
            } catch (IOException e) {
                logger.error(e.getMessage());
                throw  e;
            }
        } else {
            try {
                reader = new InputStreamReader(connection.getInputStream());
            } catch (IOException e) {
                logger.error(e.getMessage());
                throw  e;
            }
        }

        // Empty char value
        int ch;

        // String Builder to add to the final string
        StringBuilder stringBuilder = new StringBuilder();

        // Appending the data to a String Builder
        while (true) {
            try {
                assert reader != null;
                ch = reader.read();
                if (ch == -1) {
                    return stringBuilder.toString();
                }

                stringBuilder.append((char) ch);
            } catch (IOException e) {
                logger.error(e.getMessage());
                throw  e;
            }
        }
    }

    /**
     * Sets the headers with the given connection
     * @param connection The HttpURLConnection connection
     * @param headers And headers in the form of a 2-dimensional array
     */
    public static void setHeaders(HttpURLConnection connection, String[][] headers) {
        final Map<String, String> mapHeaders = new HashMap<>(headers.length);
        for (String[] map : headers) {
            mapHeaders.put(map[0], map[1]);
        }

        mapHeaders.forEach(connection::setRequestProperty);
    }

    /**
     * Direct get method, only uses the URL and any provided headers
     * @param url URL for the GET request
     * @param headers Headers in the form of a 2-dimensional array
     * @return Output of the request as a String
     */
    public  String get(String url, String[][] headers) throws IOException {
        HttpURLConnection connection;

        try {
            connection = (HttpURLConnection) new URL(url).openConnection();
            connection.setRequestMethod(Constants.GET);

            connection.setConnectTimeout(Constants.STANDARDTIMEOUT);
            connection.setReadTimeout(Constants.STANDARDTIMEOUT);

            if (headers != null) setHeaders(connection, headers);

            return read(connection);
        } catch (IOException e) {
            logger.error(e.getMessage());
            throw  e;
        }
    }

    /**
     * Method to get the response headers and return them as a regular Map
     * @return Mapped response headers
     */
    public Map<String, String> getResponseHeaders() {
        Map<String, String> mapHeaders = new HashMap<>();
        this.headers.forEach((key, value) -> value.forEach(k -> mapHeaders.put(k, key)));
        return mapHeaders;
    }
}