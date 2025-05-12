-- phpMyAdmin SQL Dump
-- version 2.11.6
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: May 11, 2025 at 04:46 AM
-- Server version: 5.0.51
-- PHP Version: 5.2.6

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `poisoning_attack`
--

-- --------------------------------------------------------

--
-- Table structure for table `pa_admin`
--

CREATE TABLE `pa_admin` (
  `username` varchar(20) NOT NULL,
  `password` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `pa_admin`
--

INSERT INTO `pa_admin` (`username`, `password`) VALUES
('admin', 'admin');

-- --------------------------------------------------------

--
-- Table structure for table `pa_data`
--

CREATE TABLE `pa_data` (
  `id` int(11) NOT NULL,
  `mid` int(11) NOT NULL,
  `bid` int(11) NOT NULL,
  `image_file` varchar(50) NOT NULL,
  `model` varchar(50) NOT NULL,
  `label_name` varchar(30) NOT NULL,
  `hash1` varchar(100) NOT NULL,
  `uname` varchar(20) NOT NULL,
  `status` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `pa_data`
--


-- --------------------------------------------------------

--
-- Table structure for table `pa_label`
--

CREATE TABLE `pa_label` (
  `id` int(11) NOT NULL,
  `mid` int(11) NOT NULL,
  `label_name` varchar(30) NOT NULL,
  `uname` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `pa_label`
--


-- --------------------------------------------------------

--
-- Table structure for table `pa_model`
--

CREATE TABLE `pa_model` (
  `id` int(11) NOT NULL,
  `model` varchar(50) NOT NULL,
  `model_file` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `pa_model`
--


-- --------------------------------------------------------

--
-- Table structure for table `pa_trainer`
--

CREATE TABLE `pa_trainer` (
  `id` int(11) NOT NULL,
  `name` varchar(20) NOT NULL,
  `mobile` bigint(20) NOT NULL,
  `email` varchar(40) NOT NULL,
  `location` varchar(50) NOT NULL,
  `uname` varchar(20) NOT NULL,
  `pass` varchar(20) NOT NULL,
  `create_date` varchar(20) NOT NULL,
  `status` int(11) NOT NULL,
  `dstatus` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `pa_trainer`
--


-- --------------------------------------------------------

--
-- Table structure for table `pa_user`
--

CREATE TABLE `pa_user` (
  `id` int(11) NOT NULL,
  `name` varchar(20) NOT NULL,
  `mobile` bigint(20) NOT NULL,
  `email` varchar(40) NOT NULL,
  `location` varchar(50) NOT NULL,
  `uname` varchar(20) NOT NULL,
  `pass` varchar(20) NOT NULL,
  `create_date` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `pa_user`
--

