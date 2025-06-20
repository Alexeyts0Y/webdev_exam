-- MySQL dump 10.13  Distrib 8.0.42, for Linux (x86_64)
--
-- Host: localhost    Database: tsoy_exam
-- ------------------------------------------------------
-- Server version	8.0.42-0ubuntu0.24.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `adoptions`
--

DROP TABLE IF EXISTS `adoptions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `adoptions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `application_date` datetime NOT NULL,
  `status` enum('PENDING','ACCEPTED','REJECTED','REJECTED_ADOPTED') NOT NULL,
  `contact_info` varchar(200) NOT NULL,
  `animal_id` int NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_adoptions_animal_id_animals` (`animal_id`),
  KEY `fk_adoptions_user_id_users` (`user_id`),
  CONSTRAINT `fk_adoptions_animal_id_animals` FOREIGN KEY (`animal_id`) REFERENCES `animals` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_adoptions_user_id_users` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `adoptions`
--

LOCK TABLES `adoptions` WRITE;
/*!40000 ALTER TABLE `adoptions` DISABLE KEYS */;
INSERT INTO `adoptions` VALUES (4,'2025-06-20 11:18:12','PENDING','88005553535',16,3);
/*!40000 ALTER TABLE `adoptions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` VALUES ('9f470159873e');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `animals`
--

DROP TABLE IF EXISTS `animals`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `animals` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `description` text NOT NULL,
  `age_months` int NOT NULL,
  `breed` varchar(100) NOT NULL,
  `gender` varchar(20) NOT NULL,
  `status` enum('AVAILABLE','ADOPTION','ADOPTED') NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `animals`
--

LOCK TABLES `animals` WRITE;
/*!40000 ALTER TABLE `animals` DISABLE KEYS */;
INSERT INTO `animals` VALUES (3,'Ева','<p>Хорошая кошка</p>',5,'Тайская','female','AVAILABLE','2025-06-20 10:37:53'),(5,'Кирилл','<p>Хороший кот</p>',4,'Сибирская','male','AVAILABLE','2025-06-20 10:59:36'),(6,'Лев','<p>Хороший кот</p>',6,'Рагамаффин','male','AVAILABLE','2025-06-20 11:00:19'),(7,'Екатерина','<p>Хорошая кошка</p>',12,'Персидская','female','AVAILABLE','2025-06-20 11:01:27'),(8,'Вероника','<p>Хорошая кошка</p>',8,'Домашняя','female','AVAILABLE','2025-06-20 11:02:12'),(9,'Виктория','<p>Хорошая собака</p>',9,'Далматин','female','AVAILABLE','2025-06-20 11:02:46'),(10,'Матвей','<p>Хороший пес</p>',10,'Бульдог','male','AVAILABLE','2025-06-20 11:03:14'),(11,'Александра','<p>Хорошая кошка</p>',14,'Бразильская','female','AVAILABLE','2025-06-20 11:03:53'),(12,'Фёдор','<p>Хороший пес</p>',8,'Бигль','male','AVAILABLE','2025-06-20 11:04:23'),(13,'Ясмина','<p>Хорошая кошка</p>',7,'Бенгальская','female','AVAILABLE','2025-06-20 11:04:59'),(16,'Элина','<p>Хорошая собака</p>',8,'Акита-ину','female','ADOPTION','2025-06-20 11:17:17'),(17,'Тузик','<p>Хороший пес</p>',13,'Дворняга','male','AVAILABLE','2025-06-20 11:17:45');
/*!40000 ALTER TABLE `animals` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `images`
--

DROP TABLE IF EXISTS `images`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `images` (
  `id` varchar(100) NOT NULL,
  `file_name` varchar(100) NOT NULL,
  `mime_type` varchar(100) NOT NULL,
  `md5_hash` varchar(100) NOT NULL,
  `object_id` int DEFAULT NULL,
  `object_type` varchar(100) DEFAULT NULL,
  `animal_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_images_md5_hash` (`md5_hash`),
  KEY `fk_images_animal_id_animals` (`animal_id`),
  CONSTRAINT `fk_images_animal_id_animals` FOREIGN KEY (`animal_id`) REFERENCES `animals` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `images`
--

LOCK TABLES `images` WRITE;
/*!40000 ALTER TABLE `images` DISABLE KEYS */;
INSERT INTO `images` VALUES ('18d3215b-9bc1-4582-bac9-a754a691e19b','jpg','image/jpeg','6438cc219c4804309843c5025a142c76',NULL,NULL,16),('44d9a18a-5fc0-42b7-bdbd-a8facc78c2cf','jpg','image/jpeg','fd1893131b2d4f18d6f9a134d6675436',NULL,NULL,3),('4891f5d7-2146-4e15-a0f0-752f831523ea','jpg','image/jpeg','e87e6452c893d7b0f20f088415201f54',NULL,NULL,13),('6a7aa953-988b-41be-aeb5-c8bfc87bfb63','jpg','image/jpeg','a56b73703eadabab9d21b2936c03a886',NULL,NULL,12),('99f40607-d3fd-4dd7-b50b-f36e5f9c919c','Tuzik.jpeg','image/jpeg','55812218d7d47e86e24ca04ca0fafd14',NULL,NULL,17),('9e2d75fa-0f07-40eb-b200-24915cc7cf8c','jpg','image/jpeg','3ede41d28b18c055b235fa2f1e301c24',NULL,NULL,5),('cbaee6ee-2d50-4c2c-a1d8-5cefbccd05d8','jpg','image/jpeg','6ee59807a2d5cc97d6c7f863d632ab32',NULL,NULL,9),('d0ccc95a-15e8-47df-9bab-d53f87b251ad','jpg','image/jpeg','0d5557e468e1e74cbe63f4a6db6710c8',NULL,NULL,8),('d3ec504a-c2cb-4ea0-8b4d-ac781ff89d41','jpg','image/jpeg','821cbc03121108f8e7cb4e0925e35f13',NULL,NULL,7),('d970ec03-09fa-41a7-9028-1dac9c83f392','jpg','image/jpeg','bdcbbde0f00815c69b4cecc80464fdaa',NULL,NULL,6),('e6c88e47-93d7-4eba-a084-bea9dc024000','jpg','image/jpeg','4b6ef2bf55c2e5f7fc51237cac211f07',NULL,NULL,11),('fdbcdff9-9df6-4d5b-9764-a5ac16f58179','jpg','image/jpeg','f6976147cf2ac6de3396cbfd2b99de17',NULL,NULL,10);
/*!40000 ALTER TABLE `images` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_roles`
--

DROP TABLE IF EXISTS `user_roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_roles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `description` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_roles`
--

LOCK TABLES `user_roles` WRITE;
/*!40000 ALTER TABLE `user_roles` DISABLE KEYS */;
INSERT INTO `user_roles` VALUES (1,'admin','Администратор с полными правами доступа'),(2,'moderator','Модератор с ограниченными правами доступа'),(3,'user','Обычный пользователь с базовыми правами');
/*!40000 ALTER TABLE `user_roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `login` varchar(100) NOT NULL,
  `password_hash` varchar(200) NOT NULL,
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(100) NOT NULL,
  `middle_name` varchar(100) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `role_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_users_login` (`login`),
  KEY `fk_users_role_id_user_roles` (`role_id`),
  CONSTRAINT `fk_users_role_id_user_roles` FOREIGN KEY (`role_id`) REFERENCES `user_roles` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'admin','scrypt:32768:8:1$s0CmY3R9mWSLiPgA$e694708a27b84a376c44d329919606b71c3eee306fa7ac231c16be8b67c21916245d53bf48f9e09a17f8a79e01a6775ac85949cbe15dec97366b3f918d384ccd','Иван','Иванов','Иванович','2025-06-18 14:21:09',1),(2,'moderator','scrypt:32768:8:1$LtzTZHCmGxkvEHJD$bab829a717ef58239bad3beceee37dca398e03565dab36153fb916e75150cf8eebb1d07f573541ad409ba9d775f47e57e4de9c66fefea216dcca18905db9768f','Петр','Петров','Петрович','2025-06-18 14:21:09',2),(3,'user','scrypt:32768:8:1$aNHDoKamKSdR8el9$0095ab936b243a3d5724caef80e250982f15d9caf591ca0614a10219bcdbfcbe39ee4662ce723b47a9d1cbe87b09b8701976773e82d8adfa7749b815d50e5ea3','Сергей','Сергеев','Сергеевич','2025-06-18 14:21:10',3);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-06-20 11:51:39
