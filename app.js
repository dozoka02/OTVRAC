const express = require('express');
const fs = require('fs');
const csv = require('csv-parser');
const app = express();
const PORT = 3000;

app.use(express.static(__dirname));

app.get('/data/csv', (req, res) => {
   const results = [];
   let isFirstRow = true;

   fs.createReadStream('./data/podaci.csv')
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

app.listen(PORT, () => {
   console.log(`Server is running on http://localhost:${PORT}`);
});
