const express = require('express');
const fs = require('fs');
const path = require('path');
const { Pool } = require('pg');
const { auth } = require('express-openid-connect');
require('dotenv').config();

const app = express();
const PORT = 3000;

// Database configuration
const pool = new Pool({
   user: 'postgres',
   host: 'localhost',
   database: 'labos',
   password: 'bazepodataka',
   port: 5432,
});

// Auth0 configuration
const config = {
   authRequired: false,
   auth0Logout: true,
   secret: process.env.AUTH0_CLIENT_SECRET,
   baseURL: `http://localhost:${PORT}`,
   clientID: process.env.AUTH0_CLIENT_ID,
   issuerBaseURL: `https://${process.env.AUTH0_DOMAIN}`,
};

// Middleware for Auth0
app.use(auth(config));

// Middleware to check authentication
const isAuthenticated = (req, res, next) => {
   if (req.oidc.isAuthenticated()) {
      return next();
   }
   res.status(401).send('Unauthorized: Please log in to access this resource.');
};

// Serve static files
app.use(express.static(__dirname));

// Endpoint to generate and download CSV (requires authentication)
app.get('/generate-csv', isAuthenticated, async (req, res) => {
   const outputPath = path.join(__dirname, 'data.csv');
   const query = `
      COPY (
         SELECT books.title, string_agg(authors.name || ', ' || authors.surname, ';') as author, books.genres, 
                books.year_of_original_publication, books.year_of_publication, books.isbn13, books.isbn10, books.publisher, 
                books.num_of_pages, books.language, books.series 
         FROM books 
         JOIN authors ON books.author_id = authors.author_id 
         GROUP BY books.isbn13
      ) TO '${outputPath}' WITH DELIMITER ',' CSV HEADER;
   `;
   try {
      await pool.query(query);
      res.download(outputPath);
   } catch (err) {
      res.status(500).send(`Error generating CSV: ${err.message}`);
   }
});

// Endpoint to generate and download JSON (requires authentication)
app.get('/generate-json', isAuthenticated, async (req, res) => {
   const outputPath = path.join(__dirname, 'data.json');
   const query = `
      COPY (
         SELECT array_to_json(array_agg(row_to_json(t))) 
         FROM (
            SELECT books.title, 
                   COALESCE(
                     json_agg(json_build_object('name', authors.name, 'surname', authors.surname)) 
                     FILTER (WHERE authors.author_id IS NOT NULL), '[]'
                   ) AS autor, 
                   books.genres, books.year_of_original_publication, books.year_of_publication, books.isbn13, 
                   books.isbn10, books.publisher, books.num_of_pages, books.language, books.series 
            FROM books 
            JOIN authors ON books.author_id = authors.author_id 
            GROUP BY books.title, books.genres, books.year_of_original_publication, books.year_of_publication, 
                     books.isbn13, books.isbn10, books.publisher, books.num_of_pages, books.language, books.series
         ) t
      ) TO '${outputPath}';
   `;
   try {
      await pool.query(query);
      res.download(outputPath);
   } catch (err) {
      res.status(500).send(`Error generating JSON: ${err.message}`);
   }
});

// Existing endpoint to serve CSV data as JSON (requires authentication)
app.get('/data/csv', isAuthenticated, (req, res) => {
   const results = [];
   let isFirstRow = true;

   fs.createReadStream('./podaci.csv')
      .pipe(csv({
         separator: ',',
         skipEmptyLines: true,
         headers: [
            'title', 'author', 'genres', 'year_of_original_publication',
            'year_of_publication', 'isbn13', 'isbn10', 'publisher',
            'num_of_pages', 'language', 'series'
         ]
      }))
      .on('data', (data) => {
         if (isFirstRow) {
            isFirstRow = false;
            return;
         }
         data.genres = data.genres.replace(/{|}/g, '').split(',').map(item => item.trim());
         results.push(data);
      })
      .on('end', () => {
         res.json(results);
      });
});

// Endpoint to fetch data with filters (requires authentication)
app.get('/fetch-data', isAuthenticated, async (req, res) => {
   const { search, attribute } = req.query;

   let query = `
      SELECT books.title, 
             string_agg(authors.name || ' ' || authors.surname, ';') as author, 
             books.genres, 
             books.year_of_original_publication, 
             books.year_of_publication, 
             books.isbn13, 
             books.isbn10, 
             books.publisher, 
             books.num_of_pages, 
             books.language, 
             books.series
      FROM books
      JOIN authors ON books.author_id = authors.author_id
      GROUP BY books.title, books.genres, books.year_of_original_publication, 
               books.year_of_publication, books.isbn13, books.isbn10, 
               books.publisher, books.num_of_pages, books.language, books.series
   `;

   // Apply filters if provided
   if (search && attribute) {
      query += ` HAVING LOWER(${attribute}) LIKE '%' || $1 || '%'`;
   }

   try {
      const { rows } = await pool.query(query, search && attribute ? [search] : []);
      res.json(rows);
   } catch (err) {
      res.status(500).send(`Error fetching data: ${err.message}`);
   }
});

// Authentication status endpoint
app.get('/auth-status', (req, res) => {
   res.json({ authenticated: req.oidc.isAuthenticated() });
});

// Start server
app.listen(PORT, () => {
   console.log(`Server is running on http://localhost:${PORT}`);
});
