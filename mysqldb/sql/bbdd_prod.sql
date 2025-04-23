-- MySQL dump 10.13  Distrib 8.0.32, for Win64 (x86_64)
--
-- Host: localhost    Database: sen4farming
-- ------------------------------------------------------
-- Server version	8.0.31

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `ayudausuario`
--

DROP TABLE IF EXISTS `ayudausuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ayudausuario` (
  `id` int NOT NULL AUTO_INCREMENT,
  `body` varchar(255) NOT NULL,
  `description` varchar(255) NOT NULL,
  `title` varchar(255) NOT NULL,
  `url` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=55 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ayudausuario`
--

LOCK TABLES `ayudausuario` WRITE;
/*!40000 ALTER TABLE `ayudausuario` DISABLE KEYS */;
INSERT INTO `ayudausuario` VALUES (1,'','','','/userguide/ctr/home'),(2,'','','','/userguide/ctr/ctr/users/login'),(8,'','','','/userguide/ctr/users/userslisthelp'),(9,'','','','/userguide/ctr/users/userregistry'),(11,'','','','/userguide/ctr/users/groups/groupslist'),(12,'','','','/userguide/ctr/users/groups/groupsregister'),(20,'','','','/userguide/ctr/users/changepassw'),(21,'','','','/userguide/ctr/users/restetpassword'),(26,'','','','/userguide/ctr/copsh/newquery'),(31,'','','','/userguide/ctr/copsh/credentials'),(32,'','','','/userguide/ctr/copsh/listqueries'),(35,'','','','/userguide/ctr/copsh/evalsclist'),(36,'','','','/userguide/ctr/copsh/evalscregistry'),(38,'','','','/userguide/ctr/csv/uploadcsv'),(41,'','','','/userguide/ctr/csv/querysoc'),(44,'','','','/userguide/ctr/csv/uploadkml'),(50,'','','','/userguide/ctr/csv/lucas2018'),(51,'','','','/userguide/ctr/csv/listcsv'),(52,'','','','/userguide/ctr/csv/index'),(54,'','','','/userguide/ctr/copsh/index');
/*!40000 ALTER TABLE `ayudausuario` ENABLE KEYS */;
UNLOCK TABLES;


--
-- Table structure for table `grupos`
--

DROP TABLE IF EXISTS `grupos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `grupos` (
  `id` bigint NOT NULL,
  `active` bit(1) NOT NULL,
  `descripcion` varchar(250) DEFAULT NULL,
  `email` varchar(30) DEFAULT NULL,
  `url` varchar(250) DEFAULT NULL,
  `description_01` varchar(250) NOT NULL DEFAULT 'default',
  `description_02` varchar(250) NOT NULL DEFAULT 'default',
  `description_03` varchar(250) NOT NULL DEFAULT 'default',
  `description_04` varchar(250) NOT NULL DEFAULT 'default',
  `description_en` varchar(250) NOT NULL,
  `description_es` varchar(250) NOT NULL,
  `description_fr` varchar(250) NOT NULL,
  PRIMARY KEY (`id`,`description_02`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `grupos`
--

LOCK TABLES `grupos` WRITE;
/*!40000 ALTER TABLE `grupos` DISABLE KEYS */;
INSERT INTO `grupos` VALUES (1,_binary '','Grupo por defecto','jmafernandez@ubu.es','url','','','','','Default group','Grupo por defecto','Default group'),(2,_binary '','Grupo investigacion UBU','jmafernandez@ubu.es','url','','','','','Investigation group UBU','Grupo investigacion UBU','Investigation group UBU'),(3,_binary '','Grupo investigacion 2','eneascarneiro@gmail.com','url','default','default','default','default','Investigation group 2','Investigation group 2','Investigation group 2'),(4,_binary '','Grupo investigacion 3','eneascarneiro@gmail.com','url','default','default','default','default','Investigation group 3','Investigation group 3','Investigation group 3'),(5,_binary '','Grupo investigacion 4','eneascarneiro@gmail.com','url','default','default','default','default','Investigation group 4','Investigation group 4','Investigation group 4'),(52,_binary '\0','Grupo investigación eneas','eneascarneiro@gmail.com','eneas','','','','','Investidation group eneas','Grupo investigación eneas','Investidation group eneas');
/*!40000 ALTER TABLE `grupos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `grupos_seq`
--

DROP TABLE IF EXISTS `grupos_seq`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `grupos_seq` (
  `next_val` bigint DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `grupos_seq`
--

LOCK TABLES `grupos_seq` WRITE;
/*!40000 ALTER TABLE `grupos_seq` DISABLE KEYS */;
INSERT INTO `grupos_seq` VALUES (301);
/*!40000 ALTER TABLE `grupos_seq` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `menu`
--

DROP TABLE IF EXISTS `menu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `menu` (
  `id` int NOT NULL AUTO_INCREMENT,
  `active` int DEFAULT NULL,
  `description` varchar(255) NOT NULL,
  `app_order` int DEFAULT NULL,
  `url` varchar(255) DEFAULT NULL,
  `parent_id` int DEFAULT NULL,
  `description01` varchar(255) NOT NULL,
  `description02` varchar(255) NOT NULL,
  `description03` varchar(255) NOT NULL,
  `description04` varchar(255) NOT NULL,
  `description_en` varchar(255) NOT NULL,
  `description_es` varchar(255) NOT NULL,
  `description_fr` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `FKgeupubdqncc1lpgf2cn4fqwbc` (`parent_id`),
  CONSTRAINT `FKgeupubdqncc1lpgf2cn4fqwbc` FOREIGN KEY (`parent_id`) REFERENCES `menu` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1000000 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menu`
--

LOCK TABLES `menu` WRITE;
/*!40000 ALTER TABLE `menu` DISABLE KEYS */;
INSERT INTO `menu` VALUES (1,1,'Inicio',0,'/',999999,'Home','/userguide/ctr/home','Inicio','Inicio','Home','Inicio','Début'),(2,1,'Login',2,'/usuarios/login',999999,'Login','/userguide/ctr/ctr/users/login','','','Login','Entrar','Se connecter'),(3,0,'General',10,'',999999,'','','','','General','Genaral','générale'),(4,0,'Books',20,'/books',3,'','','','','','',''),(5,0,'Books read',30,'/booksreads',999999,'','','','','','',''),(6,0,'Books sold',40,'/bookssolds',999999,'','','','','','',''),(7,1,'Users',50,'',999999,'','','','','Users','Usuarios','utilisateur'),(8,1,'Lista de usuarios',51,'/usuarios',7,'Users / Users list','/userguide/ctr/users/userslisthelp','','','Users list','Lista de usuarios','Liste des utilisateurs'),(9,1,'Registrar usarios',59,'/usuarios/registro',999999,'Users registry','/userguide/ctr/users/userregistry','','','Users registry','Registro de  usarios','Registre des utilisateurs'),(10,0,'Groups',60,NULL,999999,'','','','','Groups','Grupos','Group'),(11,1,'Lista de Grupos',61,'/grupos',10,'Groups / Groups list','/userguide/ctr/users/groups/groupslist','','','Groups list','Lista de grupos','Liste des groupes'),(12,1,'Registrar grupo',62,'/grupos/registro',10,'','/userguide/ctr/users/groups/groupsregister','','','','',''),(13,0,'Etiquetas',70,NULL,999999,'','','','','','',''),(14,0,'Lista de etiquetas',71,'/etiquetas',13,'','','','','','',''),(15,0,'Registro',72,'/etiquetas/registro',13,'','','','','','',''),(16,0,'Catálogo',80,NULL,999999,'','','','','','',''),(17,0,'Mookup',81,'/galeria/embed',16,'','','','','','',''),(18,0,'Registro',82,'/galeria/embed/registro',16,'','','','','','',''),(19,1,'Logout',9999,'/logout',999999,'Logout','','','','Logout','Salir','Se déconnecter'),(20,1,'Cambio password',52,'/usuarios/cambiopass',7,'Users / Change password','/userguide/ctr/users/changepassword','','','Change password','Cambiar password','Changer le mot de passe'),(21,1,'Reser password',99,'/usuarios/hasOlvidadoTuPassword',999999,'Reser password','/userguide/ctr/users/resetpassword','','','Reset password','Recuperar pasword','Reset password'),(22,0,'Interfaz api test',90,NULL,999999,'','','','','Api test interface','Interfaz api test','Interfaz api test'),(23,0,'Test simple',91,'/api/test',22,'','','','','Simple test','Test simple','Test simple'),(24,0,'List test',92,'/api/testlist',22,'','','','','List test','Test de lista','List test'),(25,0,'Sentinel 2',300,NULL,999999,'','','','','Query sentinel 2','Consulta Sentinel2','Query sentinel 2'),(26,1,'New query',101,'/api/listfiles',45,'Copernicus Sentinel HUB / New Query','/userguide/ctr/copsh/newquery','','','New query','Nueva consulta','New query'),(27,0,'Procesar',302,'/api/procesar',25,'','','','','Process file','Procesar archivo','Process file'),(28,0,'Download Lucas Dataset',303,'/api/lucas/lucas2018Search',50,'','','','','Download Lucas Dataset','Descargar dataset de LUCAS','Download Lucas Dataset'),(29,1,'Projecto',1,'/project',999999,'Project details','','','','Project details','Detalles del projecto','Project details'),(30,0,'Image Viewer',150,'/visor/images',999999,'','','','','Image Viewer','Visor de imágenes','Image Viewer'),(31,1,'Sentinel credentials',150,'/api/credentials',45,'Copernicus Sentinel HUB / Sentinel credentials','/userguide/ctr/copsh/credentials','','','Sentinel credentials','Credenciales de Sentinel','Sentinel credentials'),(32,1,'My queries',100,'/filtrolistararchivos',45,'Copernicus Sentinel HUB / My Queries','/userguide/ctr/copsh/listqueries','','','My queries','Mis consultas','My queries'),(33,0,'Scripts',120,NULL,45,'','','','','Scripts','Scripts','Scripts'),(34,0,'List',101,'/filtrolistararchivos',32,'','','','','List executed queries','Listar consultas ejecutadas','List executed queries'),(35,1,'My Evalscripts',121,'/evalscript',45,'Copernicus Sentinel HUB / My Evalscripts','/userguide/ctr/copsh/evalsclist','','','My Evalscripts','Mis Evalscripts','My Evalscripts'),(36,1,'Create Evalscript',122,'/evalscript/registro',45,'Copernicus Sentinel HUB / Create Evalscript','/userguide/ctr/copsh/evalscregistry','','','Create Evalscript','Crear Evalscript','Create Evalscript'),(37,0,'Download tiff file',305,'/api/downloadtiff',32,'','','','','Download tiff file','Descargar archivo tiff','Download tiff file'),(38,1,'Upload Csv coords',4,'/upload',47,'CSV files / Upload Csv coords','/userguide/ctr/csv/uploadcsv','','','Upload csv file','Subir archivo csv','Upload csv file'),(39,0,'SOC  Files',400,'',999999,'','','','','Soc Files','Archivos SOC','Soc Files'),(40,0,'List SOC Files',402,'/uploadedfiles',39,'','','','','List SOC Files','Lista de archivos SOC','List SOC Files'),(41,1,'Query SOC',304,'/api/models/list',47,'CSV files / Query SOC','/userguide/ctr/csv/querysoc','','','Query SOC','Consulta SOC','Query SOC'),(42,0,'Data providers',350,'/',999999,'','','','','Shared SOC points','Data providers','Data providers'),(43,0,'Viev points',351,'/visor/image/lucaspoints',42,'','','','','Shared SOC points','Shared SOC points','Shared SOC points'),(44,1,'Upload kml file',3,'/upload/kml',47,'CSV files / Upload kml file','/userguide/ctr/csv/uploadkml','','','Upload kml file','Upload kml file','Upload kml file'),(45,1,'Copernicus Sentinel HUB',70,NULL,999999,'','','','','Copernicus Sentinel HUB','Copernicus Sentinel HUB','Copernicus Sentinel HUB'),(46,0,'Google Earth Engine',80,NULL,999999,'','','','','Google Earth Engine','Google Earth Engine','Google Earth Engine'),(47,1,'CSV files',90,NULL,999999,'','','','','CSV files','CSV files','CSV files'),(50,1,'Lucas',1,'/api/lucas/lucas2018Search',47,'CSV files / Lucas','/userguide/ctr/csv/lucas2018','','','Lucas','Lucas','Lucas'),(51,1,'User CSV files',2,'/uploadedfiles',47,'CSV files / User CSV files','/userguide/ctr/csv/listcsv','','','User CSV files','User CSV files','User CSV files'),(52,0,'User Guide',999,'/userguide/ctr/home',47,'CSV files / Userguide','/userguide/ctr/home/1','','','User Guide','User Guide','User Guide'),(53,0,'User Guide',999,'/userguide/ctr/home',46,'Google Earth Engine / Userguide','/userguide/ctr/home/2','','','User Guide','User Guide','User Guide'),(54,0,'User Guide',999,'/userguide/ctr/home',45,'Copernicus Sentinel HUB / Userguide','/userguide/ctr/home','','','User Guide','User Guide','User Guide'),(55,1,'Inference filter',100,NULL,999999,'','','','','Inference filter','Inference filter','Inference filter'),(56,1,'Inference filter queries',1,'/kalman/list',55,'Inference / Inferece query','/userguide/kalman','','','Inference filter queries','Inference filter queries','Inference filter queries'),(999999,1,'aa',9999999,'',999999,'','','','','','','');
/*!40000 ALTER TABLE `menu` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `menu_roles`
--

DROP TABLE IF EXISTS `menu_roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `menu_roles` (
  `menu_id` int NOT NULL,
  `roles_id` int NOT NULL,
  PRIMARY KEY (`menu_id`,`roles_id`),
  KEY `FKauv6mbpeo296vhbm7avtoi3o8` (`roles_id`),
  CONSTRAINT `FKauv6mbpeo296vhbm7avtoi3o8` FOREIGN KEY (`roles_id`) REFERENCES `role` (`id`),
  CONSTRAINT `FKq7k54hb6f3ngdbfpblwj68bhg` FOREIGN KEY (`menu_id`) REFERENCES `menu` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menu_roles`
--

LOCK TABLES `menu_roles` WRITE;
/*!40000 ALTER TABLE `menu_roles` DISABLE KEYS */;
INSERT INTO `menu_roles` VALUES (1,1),(3,1),(4,1),(5,1),(6,1),(7,1),(8,1),(10,1),(11,1),(13,1),(14,1),(15,1),(16,1),(17,1),(18,1),(19,1),(20,1),(22,1),(23,1),(24,1),(25,1),(26,1),(27,1),(28,1),(29,1),(30,1),(31,1),(32,1),(33,1),(34,1),(35,1),(36,1),(37,1),(38,1),(39,1),(40,1),(41,1),(42,1),(43,1),(44,1),(45,1),(46,1),(47,1),(50,1),(51,1),(52,1),(53,1),(54,1),(55,1),(56,1),(1,2),(4,2),(5,2),(6,2),(8,2),(10,2),(11,2),(13,2),(14,2),(15,2),(16,2),(17,2),(18,2),(19,2),(20,2),(26,2),(29,2),(31,2),(32,2),(33,2),(35,2),(36,2),(41,2),(45,2),(46,2),(47,2),(50,2),(51,2),(52,2),(53,2),(54,2),(1,3),(2,3),(9,3),(21,3),(29,3),(1,5),(3,5),(7,5),(19,5),(20,5),(25,5),(26,5),(27,5),(28,5),(29,5),(30,5),(31,5),(32,5),(33,5),(34,5),(35,5),(36,5),(37,5),(38,5),(39,5),(40,5),(41,5),(42,5),(43,5),(44,5),(45,5),(46,5),(47,5),(50,5),(51,5),(52,5),(53,5),(54,5),(55,5),(56,5);
/*!40000 ALTER TABLE `menu_roles` ENABLE KEYS */;
UNLOCK TABLES;



--
-- Table structure for table `role`
--

DROP TABLE IF EXISTS `role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `role` (
  `id` int NOT NULL AUTO_INCREMENT,
  `role_name` varchar(255) NOT NULL,
  `role_name_en` varchar(255) NOT NULL,
  `role_name_es` varchar(255) NOT NULL,
  `role_name_fr` varchar(255) NOT NULL,
  `role_name_01` varchar(255) NOT NULL,
  `role_name_02` varchar(255) NOT NULL,
  `role_name_03` varchar(255) NOT NULL,
  `role_name_04` varchar(255) NOT NULL,
  `show_on_create` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `role`
--

LOCK TABLES `role` WRITE;
/*!40000 ALTER TABLE `role` DISABLE KEYS */;
INSERT INTO `role` VALUES (1,'ROLE_ADMIN','Administrator','Administrador','Administrateur','','','','',0),(2,'ROLE_AGRICULTOR','Standard user','Usuario estandar','Utilisateur standard','','','','',1),(3,'ROLE_ANONIMOUS','Anonimous','Anonimo','Anonyme','','','','',0),(5,'ROLE_INVESTIGADOR','Researcher','Investigador','Chercheur','','','','',1);
/*!40000 ALTER TABLE `role` ENABLE KEYS */;
UNLOCK TABLES;



DROP TABLE IF EXISTS `usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario` (
  `id` bigint NOT NULL,
  `active` bit(1) NOT NULL,
  `email` varchar(50) DEFAULT NULL,
  `nombre_usuario` varchar(30) DEFAULT NULL,
  `password` varchar(250) DEFAULT NULL,
  `codigo_grupo_trabajo` bigint DEFAULT NULL,
  `token` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_usuario_email` (`email`),
  KEY `FK122iiiy7bly1gmyfrwv9orvql` (`codigo_grupo_trabajo`),
  CONSTRAINT `FK122iiiy7bly1gmyfrwv9orvql` FOREIGN KEY (`codigo_grupo_trabajo`) REFERENCES `grupos` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario`
--

LOCK TABLES `usuario` WRITE;
/*!40000 ALTER TABLE `usuario` DISABLE KEYS */;
INSERT INTO `usuario` VALUES (1,_binary '','anonimo@anonimo','ttt','$2a$10$KQWx/OEgzTNitISaN1cSd.So3HKPVgqxDxk6uHXstaGLcAZE.vIam',NULL,'0e2a540e-92b2-486b-a731-c7a40640d716'),(167,_binary '','admin@gmail.com','admin','$2a$10$KQWx/OEgzTNitISaN1cSd.So3HKPVgqxDxk6uHXstaGLcAZE.vIam',52,'0e2a540e-92b2-486b-a731-c7a40640d716'),(1951,_binary '','jmafernandez@ubu.es','jma','$2a$10$NMWO.XKIe4ayuM5NZVJn7ewrLycBXJlHGtoTKOaAgrw8ICciIhVWC',52,'0e2a540e-92b2-486b-a731-c7a40640d716'),(2001,_binary '','jose.manuel.aroca@hotmail.com','jma','$2a$10$bhGTVOXfy11JfTq6rvzaMObdGUxzB6GEXDjukiu7m8b9WsANSViZS',52,'0e2a540e-92b2-486b-a731-c7a40640d716'),(2051,_binary '','jose.manuel.aroca@gmail.com','José Manuel Aroca','$2a$10$bhGTVOXfy11JfTq6rvzaMObdGUxzB6GEXDjukiu7m8b9WsANSViZS',52,'0e2a540e-92b2-486b-a731-c7a40640d716'),(2101,_binary '','jose.manuel.aroca.fernandez@gmail.com','Jmafernandez','$2a$10$bhGTVOXfy11JfTq6rvzaMObdGUxzB6GEXDjukiu7m8b9WsANSViZS',2,'0b721305-3065-46a6-937f-43f2fe455092'),(2451,_binary '','jaf1012@alu.ubu.es','jmafernandez1','$2a$10$r7YWFS13CBOXAPsm/Py02eoZpqBDrQoFRkt3nIwmdGEKh3ZIKNEFG',1,'a09e4d02-50e5-4d94-b07b-0a9e1ba76daa'),(2551,_binary '','jmafernandez3@ubu.es','jmafernandez3','$2a$10$2fJaPtP9u3XWpcmj0a5ne.dzQmeEIrBQpWwlv38u2Jxfb41jRPdby',1,'428336c4-c95e-4049-9556-dc15dcb37766');
/*!40000 ALTER TABLE `usuario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuario_roles`
--

DROP TABLE IF EXISTS `usuario_roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario_roles` (
  `usuarios_id` bigint NOT NULL,
  `roles_id` int NOT NULL,
  PRIMARY KEY (`usuarios_id`,`roles_id`),
  KEY `FKr5p0u8r15jjo6u7xr1928hsld` (`roles_id`),
  CONSTRAINT `FKli6wslofo9n7han07s8iiwyub` FOREIGN KEY (`usuarios_id`) REFERENCES `usuario` (`id`),
  CONSTRAINT `FKr5p0u8r15jjo6u7xr1928hsld` FOREIGN KEY (`roles_id`) REFERENCES `role` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario_roles`
--

LOCK TABLES `usuario_roles` WRITE;
/*!40000 ALTER TABLE `usuario_roles` DISABLE KEYS */;
INSERT INTO `usuario_roles` VALUES (1951,1),(2551,2),(1,3),(2001,5),(2051,5),(2101,5),(2451,5);
/*!40000 ALTER TABLE `usuario_roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuario_seq`
--

DROP TABLE IF EXISTS `usuario_seq`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario_seq` (
  `next_val` bigint DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario_seq`
--

LOCK TABLES `usuario_seq` WRITE;
/*!40000 ALTER TABLE `usuario_seq` DISABLE KEYS */;
INSERT INTO `usuario_seq` VALUES (2650),(1901);
/*!40000 ALTER TABLE `usuario_seq` ENABLE KEYS */;
UNLOCK TABLES;


/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-04-23  1:20:52
