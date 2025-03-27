# Aptitude Application

## Overview

This application allows users to upload images for a question and its multiple-choice answers, extract text using Google Gemini API's OCR capabilities, and display the question with answer options for voting and tallying votes.

## Features

- Image upload for questions and multiple-choice answers
- OCR extraction using Google Gemini API
- Display extracted question and answer options
- Voting on answer options
- Tallying votes and displaying the most voted answer option(s)

## Instructions

1. **Upload Images**: Upload an image for the question and separate images for each multiple-choice answer.
2. **Extract Text**: The application will use Google Gemini API to extract text from the uploaded images.
3. **Vote**: The extracted question and answer options will be displayed, allowing users to vote on their preferred answer.
4. **Results**: The application will tally the votes and display the question along with the most voted answer option(s).

## Google Gemini API Setup

To use the Google Gemini API for OCR extraction, follow these steps:

1. Sign up for a Google Cloud account if you don't have one.
2. Enable the Google Gemini API in your Google Cloud project.
3. Obtain an API key for accessing the Google Gemini API.
4. Configure the application to use the API key for making requests to the Google Gemini API.

## Error Handling and Troubleshooting

- Ensure that the uploaded images are clear and legible for accurate OCR extraction.
- Check the console for any error messages if the OCR extraction fails.
- Verify that the Google Gemini API key is correctly configured in the application.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Instructions](#instructions)
- [Google Gemini API Setup](#google-gemini-api-setup)
- [Error Handling and Troubleshooting](#error-handling-and-troubleshooting)
