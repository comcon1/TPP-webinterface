<template>
  <div class="container">
    <h1>About TPPMKTOP project</h1>
    <p>
    The TPPMKTOP project is a web-based service designed to process molecules in PDB format and 
to return topolgy in GROMACS format. TPPMKTOP uses MySQL database with SMARTS patterns as well as 
with bonded interactions information to assign OPLS atomtypes according to chemical environment.
    </p>
    <p>
<b>History:</b> The project was initiated in 2014 in ERG Research Group in 
the Department of Biophysics, Biology Faculty, Lomonosov Moscow State University by 
<a href="https://github.com/comcon1">@comcon1</a>, 
<a href="https://github.com/pmamonov">@pmamonov</a>, 
<a href="httsp://github.com/dvzlenko">@dvzlenko</a>. 
Further it was co-developed by <a href="https://github.com/galochkina">@galochkina</a> and 
A.Mesyats. The project is redistributed under <a href="https://www.gnu.org/licenses/gpl-3.0.html">GPLv3 license</a>.
    </p>
    <p>
<b>Structure.</b> The project is represented in four repositories:
        <ul>
             <li>Main program (C++14, libopenbabel, MySQL++):
                <a href="https://github.com/TopologyPreProcessor">comcon1/TopologyPreProcessor</a>
             </li>
             <li>Docker building recipies (Docker, docker-compose):
                <a href="https://github.com/TPP-docker">comcon1/TPP-docker</a>
             </li>
             <li>Docker images (DockerHub):
                <a href="https://hub.docker.com/r/comcon1/tppcon">comcon1/tppcon</a>
             </li>
             <li>TPP-webinterface (python3, fastapi, celery, vue2):
                <a href="https://github.com/TPP-webinterface">comcon1/TPP-webinterface</a>
             </li>
        </ul>
    </p>
  </div>
</template>

<script>
const metaDescription = `
TPPMKTOP project. It allows one prettify PDB file and to 
make MD topology in OPLS-AA force field (open-source version).
`;

export default {
  metaInfo: {
    title: 'TPPMKTOP - MD topology generator',
    meta: [
      {
        name: 'description',
        content: metaDescription.trim()
      }
    ]
  }
};
</script>
