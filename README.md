# The McGill Map
DEVPOST: https://devpost.com/software/the-mcgill-map

Ever wanted to see all courses happening at a specific time and day at McGill? Well now you can!

## Install instructions

### Prerequesites
<ul>
  <li>mySQL Server</li>
  <li>mySQL Workbench</li>
  <li>Python 3.8+</li>
  <li>npm</li>
</ul>

### Instructions
<ol>
  <li>Create new schema in mySQL Workbench called "campus_w24"</li>
  <li>Set up the two .env files with the right information</li>
  <li><code>git clone https://github.com/mn297/mcgillcampus.git </code></li>
  <li><code>cd</code> to project directory</li>
  <li><code>python app.py </code></li>
  <li><code>cd mcgill_map_frontend</code></li>
  <li><code>npm i </code></li>
  <li><code>npm run build </code></li>
  <li><code>npm run dev </code></li>
  <li>Go to <code>localhost:5173</code> on your web browser</li>
</ol>
