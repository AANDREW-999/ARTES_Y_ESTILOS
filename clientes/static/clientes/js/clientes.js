document.addEventListener('DOMContentLoaded', function () {
    // Elementos del DOM
    const departamentoInput = document.querySelector('#departamento_input');
    const departamentosDatalist = document.querySelector('#departamentos_datalist');
    const deptSuggestions = document.querySelector('#dept_suggestions');
    const ciudadInput = document.querySelector('#ciudad_input');
    const ciudadesDatalist = document.querySelector('#ciudades_datalist');
    const citySuggestions = document.querySelector('#city_suggestions');
    const deptSelect = document.querySelector('select[name="departamento"]'); // select real (oculto)
    const citySelect = document.querySelector('select[name="ciudad_id"]'); // select real (oculto)

    // Evitar que el navegador muestre el desplegable nativo del datalist en departamento
    if (departamentoInput) {
        try {
            departamentoInput.removeAttribute('list');
            departamentoInput.setAttribute('autocomplete', 'off');
            // Para evitar sugerencias nativas persistentes, marcar como readonly hasta interacción
            departamentoInput.readOnly = true;
            departamentoInput.addEventListener('mousedown', function () {
                this.readOnly = false;
            });
            departamentoInput.addEventListener('focus', function () {
                // en caso de que focus ocurra sin mousedown
                this.readOnly = false;
            });
            departamentoInput.addEventListener('blur', function () {
                // volver a readonly tras breve delay para permitir clicks en sugerencias
                setTimeout(() => { try { this.readOnly = true; } catch (e) {} }, 200);
            });
        } catch (e) {
            // noop
        }
    }

    // Fallback mínimo
    const FALLBACK_CITY_MAP = {
        'Amazonas': [{ id: 1, name: 'Leticia' }],
        'Antioquia': [{ id: 2, name: 'Medellín' }]
    };

    // FULL RAW DATA embedido como respaldo si fetch no puede acceder al archivo estático
    const FULL_CITY_RAW = {
  "Amazonas": [
    "Leticia",
    "Puerto Nariño",
    "Tarapacá",
    "La Chorrera",
    "El Encanto",
    "Mirití-Paraná",
    "Amacayacu",
    "Puerto Santander"
  ],
  "Antioquia": [
    "Medellín","Abejorral","Abriaquí","Alejandría","Amagá","Amalfi","Andes","Angelópolis","Angostura","Anorí","Santafé de Antioquia","Anzá","Apartadó","Arboletes","Argelia","Armenia","Barbosa","Bello","Belmira","Briceño","Buriticá","Cañasgordas","Caracolí","Caramanta","Carepa","Carolina del Príncipe","Caucasia","Chigorodó","Cisneros","Cocorná","Concepción","Concordia","Copacabana","Dabeiba","Don Matías","Ebéjico","El Bagre","Entrerríos","Envigado","Fredonia","Frontino","Giraldo","Girardota","Gómez Plata","Granada","Guadalupe","Guarne","Guatapé","Heliconia","Hispania","Itagüí","Ituango","Jericó","Jardín","Joaquín Antonio Uribe","La Ceja","La Estrella","La Pintada","La Unión","Liborina","Maceo","Marinilla","Montebello","Murindó","Mutatá","Nariño","Natagaima","Nechí","Necoclí","Olaya","Peñol","Peque","Piedras","Pueblorrico","Puerto Berrío","Puerto Nare","Puerto Triunfo","Remedios","Retiro","Rionegro","Sabanalarga","Sabaneta","Salgar","San Andrés de Cuerquia","San Carlos","San Francisco","San Jerónimo","San José de la Montaña","San Juan de Urabá","San Luis","San Pedro","San Pedro de Urabá","San Rafael","San Roque","San Vicente","Santa Bárbara","Santa Rosa de Osos","Santo Domingo","Segovia","Sonson","Sonsón","Sopetrán","Tamesis","Tarso","Titiribí","Toledo","Turbo","Urrao","Valdivia","Valparaíso","Vegachí","Venecia","Vigía del Fuerte","Yalí","Yarumal","Yolombó","Yondo","Zaragoza"
  ],
  "Arauca": [
    "Arauca","Arauquita","Cravo Norte","Fortul","Puerto Rondón","Saravena","Tame"
  ],
  "Atlántico": [
    "Barranquilla","Baranoa","Campo de la Cruz","Candelaria","Galapa","Juan de Acosta","Luruaco","Malambo","Manatí","Palmar de Varela","Piojó","Polonuevo","Ponedera","Puerto Colombia","Repelón","Sabanagrande","Sabanalarga","Santa Lucía","Santo Tomás","Soledad","Suan"
  ],
  "Bolívar": [
    "Cartagena","Achí","Altos del Rosario","Arenal","Arjona","Arroyohondo","Barranco de Loba","Calamar","Cantagallo","Cicuco","Clemencia","Córdoba","El Carmen de Bolívar","El Guamo","El Peñón","Hatillo de Loba","Magangue","Mahates","Margarita","María la Baja","Mompós","Montecristo","Morales","Norosí","Pinillos","Regidor","Rio Viejo","San Cristóbal","San Estanislao","San Fernando","San Jacinto","San Jacinto del Cauca","San Juan Nepomuceno","San Martín de Loba","San Pablo","Santa Catalina","Santa Rosa del Sur","Simití","Soplaviento","Talaigua Nuevo","Tiquisio","Turbaco","Turbaná","Villanueva","Zambrano"
  ],
  "Boyacá": [
    "Tunja","Almeida","Aquitania","Arcabuco","Belén","Berbeo","Betéitiva","Boavita","Boyacá","Briceño","Buenavista","Busbanzá","Caldas","Campohermoso","Cerinza","Chinavita","Chiquinquirá","Chíquiza","Chiscas","Chivor","Chíquiza","Ciénega","Cómbita","Coper","Corrales","Covarachía","Cubará","Cucaita","Cuítiva","Duitama","El Cocuy","El Espino","Firavitoba","Floresta","Gachantivá","Gachantivá","Gameza","Garagoa","Guacamayas","Guateque","Guayatá","Güicán","Iza","Jenesano","Jericó","La Capilla","La Uvita","La Victoria","Labranzagrande","Macanal","Maripí","Mongua","Monguí","Moniquirá","Motavita","Muzo","Nobsa","Nuevo Colón","Oicatá","Otanche","Pachavatá","Paipa","Pajarito","Panqueba","Pauna","Paya","Paz de Río","Pesca","Pisba","Puerto Boyacá","Quípama","Ramiriquí","Ráquira","Rondón","Saboyá","Sáchica","Samacá","San Eduardo","San José de Pare","San Luis de Gaceno","San Mateo","San Miguel de Sema","San Pablo de Borbur","Sántana","Santa María","Santa Rosa de Viterbo","Santa Sofía","Sativanorte","Sativasur","Siachoque","Soatá","Socha","Sogamoso","Somondoco","Sora","Soracá","Sotaquirá","Susacón","Sutamarchán","Sutatenza","Tasco","Tenza","Tibaná","Tibasosa","Tinjacá","Tipacoque","Toca","Togasá","Tópaga","Tota","Tununguá","Turmequé","Tuta","Tutazá","Úmbita","Ventaquemada","Viracachá","Zetaquirá"
  ],
  "Caldas": [
    "Manizales","Aguadas","Anserma","Aranzazu","Belalcázar","Chinchina","Filadelfia","La Dorada","La Merced","Manzanares","Marmato","Marquetalia","Marulanda","Neira","Norcasia","Pácora","Palestina","Pensilvania","Riosucio","Risaralda","Risaralda (Municipio)","Salamina","Samaná","San José","Supía","Victoria","Villamaría","Viterbo"
  ],
  "Caquetá": [
    "Florencia","Albania","Belén de los Andaquies","Cartagena del Chairá","Curillo","El Doncello","El Paujil","Montañita","Morelia","Puerto Rico","San José del Fragua","San Vicente del Caguán","Solano","Solita","Valparaíso"
  ],
  "Casanare": [
    "Yopal","Aguazul","Casanare (Municipio)","Chámeza","Hato Corozal","La Salina","Maní","Monterrey","Nunchía","Orocué","Paz de Ariporo","Pore","Recetor","Sabanalarga","San Luís de Palenque","Tauramena","Trinidad","Villanueva"
  ],
  "Cauca": [
    "Popayán","Almaguer","Argelia","Balboa","Bolívar","Buesaco","Cajibío","Caldas","Caloto","Corinto","El Tambo","Florencia (Cauca)","Guachené","Guapí","Inzá","Jambaló","La Sierra","La Vega","López de Micay","Mercaderes","Miranda","Morales (Cauca)","Padilla","Patía","Piamonte","Piendamó","Puerto Tejada","Puracé","Rosas","San Sebastián","Santa Rosa (Cauca)","Santander de Quilichao","Siberia","Silvia","Sotará","Suárez","Sucre (Cauca)","Timbío","Timbiquí","Toribío","Totoró","Villa Rica","Villa Rica (Cauca)"
  ],
  "Cesar": [
    "Valledupar","Aguachica","Agustín Codazzi","Astrea","Becerril","Bosconia","Chimichagua","Chiriguaná","Curumaní","El Copey","El Paso","Gamarra","González","La Gloria","La Jagua de Ibirico","Manaure","Pailitas","Pelaya","Pueblo Bello","Río de Oro","San Alberto","San Diego","San Martín","Tamalameque"
  ],
  "Chocó": [
    "Quibdó","Acandí","Alto Baudó","Bagadó","Bahía Solano","Bajo Baudó","Bojayá","Carmen del Darién","Cértegui","Condoto","El Carmen de Atrato","El Cantón de San Pablo","El Carmen del Darién","Istmina","Juradó","Lloró","Medio Atrato","Medio San Juan","Nóvita","Nuquí","Pizarra","Ríosucio","Riosucio (Chocó)","San Juan de Urabá","Sipí","Tadó","Unguía","Unión Panamericana"
  ],
  "Córdoba": [
    "Montería","Ayapel","Buenavista","Canalete","Cereté","Chimá","Chinú","Ciénaga de Oro","Cotorra","La Apartada","Lorica","Los Córdobas","Momil","Montelíbano","Moñitos","Planeta Rica","Pueblo Nuevo","Puerto Escondido","Puerto Libertador","Purísima","Sahagún","San Andrés de Sotavento","San Antero","San Bernardo del Viento","San Carlos","San José de Uré","San Pelayo","Tierralta","Tuchín","Valencia"
  ],
  "Cundinamarca": [
    "Bogotá","Facatativá","Funza","Madrid","Mosquera","Soacha","Zipaquirá","Chía","Fusagasugá","Girardot","Ubaté","Tocancipá","Cota","La Calera","Sesquilé","Nemocón","Sopó","Sibaté","Fómeque","Zipacón","El Rosal","Gachancipá","Gachetá","Guasca","Quetame","Cajicá","Chocontá","Anapoima","Apulo","Arbeláez","Armenia (Cundinamarca)","Beltrán","Bituima","Bojacá","Cabrera","Caparrapí","Carmen de Carupa","Chaguaní","Chipaque","Choachí","Cubarral","El Colegio","Fúquene","Guaduas","La Mesa","La Palma","Lenguazaque","Nariño (Cundinamarca)","Nemocón","Nilo","Nimaima","Nocaima","Pacho","Pandi","Paratebueno","Pasca","Puerto Salgar","Pulí","Quipile","Ricaurte","Rionegro (Cundinamarca)","Ricaurte","San Antonio del Tequendama","San Bernardo","San Cayetano","San Juan de Rioseco","Sasaima","Sibaté","Silvania","Subachoque","Susa","Sutatausa","Tabio","Tocaima","Tocancipá","Tocancipá","Tena","Tibacuy","Tibirita","Toca","Tocancipá","Ungía"
  ],
  "Guainía": [
    "Inírida"
  ],
  "Guaviare": [
    "San José del Guaviare"
  ],
  "Huila": [
    "Neiva","Acevedo","Agrado","Aipe","Algeciras","Altamira","Baraya","Campoalegre","Colombia (Huila)","Coello","Elías","Garzón","Gigante","Guadalupe","Hobo","Íquira","Iquira","Isnos","La Argentina","La Plata","Nátaga","Oporapa","Paicol","Palermo","Palestina (Huila)","Pital","Pitalito","Rivera","Saladoblanco","Santa María","Suaza","Tarqui","Tello","Teruel","Tesalia","Timaná","Villavieja","Yaguará"
  ],
  "La Guajira": [
    "Riohacha","Maicao","Manaure","Uribia","Dibulla","Barrancas","Distracción","El Molino","Fonseca"
  ],
  "Magdalena": [
    "Santa Marta","Ciénaga","Aracataca","Ariguaní","Bosconia","El Banco","El Piñón","Fundación","Guamal","Nueva Granada","Pedraza","Pijiño del Carmen","Pivijay","Plato","Remolino","Sabanas de San Ángel","Salamina","San Sebastián de Buenavista","San Zenón","Santa Ana","Santa Bárbara de Pinto","Sitionuevo","Tenerife","Zapayán"
  ],
  "Meta": [
    "Villavicencio","Acacías","Cabuyaro","Castilla la Nueva","Cubarral","Cumaral","El Calvario","El Castillo","El Dorado","Fuente de Oro","Granada","Guamal","Mapiripán","Mesetas","Puerto Concordia","Puerto Gaitán","Puerto Lleras","Puerto López","Puerto Rico","Restrepo","San Carlos de Guaroa","San Juan de Arama","San Juanito","San Martín","Uribe","Vista Hermosa"
  ],
  "Nariño": [
    "Pasto","Tumaco","Aldana","Ancuya","Barbacoas","Buesaco","Cumbal","Chachagüí","Colón (Nariño)","Consacá","Contadero","Córdoba (Nariño)","El Charco","El Peñol","El Rosario","Funes","Guachucal","Guaitarilla","Gualmatán","Iles","Imués","La Cruz","La Florida","La Llanada","La Unión (Nariño)","Leiva","Linares","Los Andes (formerly or known as),","Magüi Payán","Mallama","Mosquera","Olaya Herrera","Órdorica","Pasto","Policarpa","Potosí","Providencia (Nariño)","Puerres","Pupiales","Ricaurte","Roberto Payán","Samaniego","Sandona","San Bernardo","San Lorenzo","San Pablo (Nariño)","Santa Bárbara (Nariño)","Santacruz","Sapuyes","Taminango","Túquerres","Yacuanquer"
  ],
  "Norte de Santander": [
    "Cúcuta","Arboledas","Bochalema","Bucarasica","Cáchira","Chinácota","Chitagá","Convención","Cucutilla","Durania","El Carmen","El Tarra","El Zulia","Gramalote","Hacarí","Herrán","La Esperanza","La Playa de Belén","Labateca","Los Patios","Mutiscua","Ocaña","Pamplona","Pamplonita","Puerto Santander","Ragonvalia","Salazar de Las Palmas","San Cayetano","Santiago","Sardinata","Silos","Teorama","Tibu","Toledo"
  ],
  "Putumayo": [
    "Mocoa","Colón (Putumayo)","Orito","Puerto Asís","Puerto Caicedo","Puerto Guzmán","Puerto Leguízamo","San Francisco","San Miguel","Santiago (Putumayo)","Sibundoy","Valle del Guamuez","Villagarzón"
  ],
  "Quindío": [
    "Armenia","Buenavista (Quindío)","Calarcá","Circasia","Córdoba (Quindío)","Filandia","Génova","La Tebaida","Montenegro","Pijao","Quimbaya","Salento"
  ],
  "Risaralda": [
    "Pereira","Apía","Balboa (Risaralda)","Belén de Umbría","Dosquebradas","Guática","La Celia","La Virginia","Marsella","Mistrató","Pueblo Rico","Quinchía","Santa Rosa de Cabal","Santuario"
  ],
  "San Andrés y Providencia": [
    "San Andrés","Providencia","Santa Catalina"
  ],
  "Santander": [
    "Bucaramanga","Aguada","Albania (Santander)","Aratoca","Barbosa (Santander)","Barichara","Barrancabermeja","Betulia (Santander)","Bolívar (Santander)","Cabrera (Santander)","California (Santander)","Capitanejo","Carcasí","Cepitá","Cerrito (Santander)","Charalá","Charta","Chima","Chipatá","Cimitarra","Concepción (Santander)","Confines","Contratación","Coromoro","Curití","El Carmen de Chucurí","El Guacamayo","El Peñón (Santander)","El Playón","El Socorro","Encino (Santander)","Enciso","Florián","Floridablanca","Galán","Gámbita","Girón","Guaca","Guadalupe (Santander)","Guapotá","Guavatá","Güepsa","Hato","Jesús María","Jordán","La Belleza","Landázuri","La Paz (Santander)","Lebrija (Santander)","Los Santos","Macaravita","Málaga (Santander)","Matanza","Mogotes","Molagavita","Ocamonte","Oiba","Onzaga","Palmar","Palmas del Socorro","Páramo","Piedecuesta","Pinchote","Puente Nacional","Puerto Parra","Puerto Wilches","Rionegro (Santander)","Sabana de Torres","San Andrés (Santander)","San Benito","San Gil","San Joaquín","San José de Miranda","San Miguel","San Vicente de Chucurí","Santa Bárbara (Santander)","Santa Helena del Opón","Simacota","Socorro","Sogamoso (note: Sogamoso is Boyacá)","Suaita","Susacón","Tona","Vélez","Vetas","Villanueva (Santander)","Zapatoca"
  ],
  "Sucre": [
    "Sincelejo","Buenavista (Sucre)","Caimito (Sucre)","Colosó","Corozal","Coveñas","Chalán","El Roble","Galeras","Guaranda","La Unión (Sucre)","Los Palmitos","Majagual","Morroa","Ovejas","Sampués","San Benito Abad","San Juan de Betulia","San Marcos","San Onofre","San Pedro","Sincé","Santiago de Tolú","Tolú Viejo"
  ],
  "Tolima": [
    "Ibagué","Alpujarra","Alvarado","Ambalema","Anzoátegui","Armero (Guayabal)","Ataco","Atencingo","Coello","Coyaima","Cunday","Dolores","El Espinal","Falan","Flandes","Fresno","Gaitania","Guamo","Herveo","Icononzo","Ibagué","Lérida","Líbano","Mariquita","Melgar","Murillo","Natagaima","Ortega","Palocabildo","Piedras","Planadas","Prado","Purificación","Rioblanco","Roncesvalles","Rovira","Saldaña","San Antonio","San Luis","Santa Isabel","Suárez","Valle de San Juan","Venadillo","Villarrica"
  ],
  "Valle del Cauca": [
    "Cali","Alcalá","Andalucía","Ansermanuevo","Argelia (Valle)","Bolívar (Valle)","Buenaventura","Bugalagrande","Caicedonia","Candelaria","Cartago","Dagua","El Águila","El Cairo","El Cerrito","El Dovio","Florida","Ginebra","Guacarí","Jamundí","La Cumbre","La Unión","La Victoria","Obando","Palmira","Pradera","Restrepo","Riofrío","Roldanillo","San Pedro","Sevilla","Toro","Trujillo","Tulúa","Ulloa","Versalles","Vijes","Yotoco","Yumbo","Zarzal"
  ],
  "Vaupés": [
    "Mitú","Caruru","Pacoa","Papunahua","Taraíra"
  ],
  "Vichada": [
    "Puerto Carreño","Cumaribo","La Primavera","Santa Rosalía","San José de Ocune"
  ]
};

    let CITY_MAP = FALLBACK_CITY_MAP;
    let deptOriginalOptions = []; // { value, text }
    let currentCityOptions = []; // { id, name }

    // Normalize JSON (espera objeto { dept: [ 'ciudad', ... ] } o lista de objetos)
    function normalizeCityData(raw) {
        const result = {};
        if (!raw) return FALLBACK_CITY_MAP;
        if (Array.isArray(raw)) {
            raw.forEach((d, i) => {
                const name = d.departamento || d.name || d.nombre || d.departamento_nombre || d.id || '';
                const list = d.municipios || d.municipios || d.ciudades || d.municipios_nombre || d.id || [];
                if (!name) return;
                result[name] = [];
                if (Array.isArray(list)) {
                    list.forEach((m, j) => {
                        const cityName = (typeof m === 'string') ? m : (m.nombre || m.municipio || m.name || '');
                        result[name].push({ id: (i * 2000) + j + 1, name: cityName });
                    });
                }
            });
            return result;
        }
        if (typeof raw === 'object') {
            Object.keys(raw).forEach((dept, idx) => {
                const list = raw[dept];
                result[dept] = [];
                if (Array.isArray(list)) {
                    list.forEach((item, j) => {
                        if (typeof item === 'string') {
                            result[dept].push({ id: (idx * 2000) + j + 1, name: item });
                        } else if (typeof item === 'object') {
                            if (item.id && item.name) result[dept].push({ id: item.id, name: item.name });
                            else if (item.nombre || item.municipio || item.name) result[dept].push({ id: (idx * 2000) + j + 1, name: item.nombre || item.municipio || item.name });
                        }
                    });
                }
            });
            return result;
        }
        return FALLBACK_CITY_MAP;
    }

    function normalizeString(s) {
        if (!s) return '';
        return String(s).normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase().trim();
    }

    // Cargar JSON local (ruta estática) y aplicar normalize
    async function loadCityJson() {
        const local = '/static/clientes/data/colombia_municipios.json';
        try {
            const res = await fetch(local, { cache: 'no-cache' });
            if (res.ok) {
                const data = await res.json();
                CITY_MAP = normalizeCityData(data);
                console.info('city json cargado local. departamentos=', Object.keys(CITY_MAP).length);
                return;
            }
            console.warn('city json: respuesta no OK', res.status);
        } catch (err) {
            console.warn('city json: error cargando local', err);
        }
        // Si no se pudo cargar el archivo estático, usar FULL_CITY_RAW (embed) como fallback
        try {
            CITY_MAP = normalizeCityData(FULL_CITY_RAW);
            console.info('city json: usando FULL_CITY_RAW embedido. departamentos=', Object.keys(CITY_MAP).length);
            return;
        } catch (err) {
            console.warn('city json: fallo al usar FULL_CITY_RAW', err);
        }
        // Mantener fallback mínimo si todo falla
        CITY_MAP = CITY_MAP || FALLBACK_CITY_MAP;
    }

    function buildDeptOptionsFromMap() {
        // Empezar con claves del CITY_MAP
        const keys = Object.keys(CITY_MAP || {}).sort((a, b) => a.localeCompare(b, 'es'));
        const mapOptions = keys.map(k => ({ value: k, text: k }));
        // Añadir también las opciones existentes del select real (si hay) y fusionar evitando duplicados
        const merged = [];
        const seen = new Set();
        if (deptSelect) {
            Array.from(deptSelect.options).forEach(o => {
                const text = o.text && o.text.trim();
                if (text && !seen.has(normalizeString(text))) {
                    merged.push({ value: o.value || text, text: text });
                    seen.add(normalizeString(text));
                }
            });
        }
        // Añadir las del map que no estén ya
        mapOptions.forEach(o => {
            if (!seen.has(normalizeString(o.text))) {
                merged.push(o);
                seen.add(normalizeString(o.text));
            }
        });
        // Orden final
        deptOriginalOptions = merged.sort((a, b) => a.text.localeCompare(b.text, 'es'));
        console.info('buildDeptOptionsFromMap: opciones totales=', deptOriginalOptions.length);
    }

    function populateDeptDatalist() {
        if (!departamentosDatalist) return;
        departamentosDatalist.innerHTML = '';
        deptOriginalOptions.forEach(o => {
            const opt = document.createElement('option');
            opt.value = o.text;
            departamentosDatalist.appendChild(opt);
        });
    }

    function populateDeptSelect() {
        if (!deptSelect) return;
        // Si el select ya tiene muchas opciones, no sobrescribir; si sólo tiene la opción vacía, rellenar
        if (deptSelect.options.length <= 1) {
            deptSelect.innerHTML = '';
            const defaultOpt = document.createElement('option');
            defaultOpt.value = '';
            defaultOpt.textContent = 'Seleccione un departamento';
            deptSelect.appendChild(defaultOpt);
            deptOriginalOptions.forEach(o => {
                const opt = document.createElement('option');
                opt.value = o.value;
                opt.text = o.text;
                deptSelect.appendChild(opt);
            });
        }
    }

    function populateCitiesForDept(deptName, selectedCityId) {
        currentCityOptions = [];
        if (!citySelect) return;
        citySelect.innerHTML = '';
        const defaultOpt = document.createElement('option');
        defaultOpt.value = '';
        defaultOpt.textContent = 'Seleccione ciudad';
        citySelect.appendChild(defaultOpt);

        if (!deptName || !CITY_MAP[deptName]) return;
        CITY_MAP[deptName].forEach((c) => {
            citySelect.appendChild(new Option(c.name, c.id));
            currentCityOptions.push({ id: c.id, name: c.name });
        });
        if (selectedCityId) citySelect.value = selectedCityId;
        populateCityDatalist();
    }

    function populateCityDatalist() {
        if (!ciudadesDatalist) return;
        ciudadesDatalist.innerHTML = '';
        currentCityOptions.slice().sort((a,b)=>a.name.localeCompare(b.name,'es')).forEach(c => {
            const opt = document.createElement('option');
            opt.value = c.name;
            ciudadesDatalist.appendChild(opt);
        });
    }

    // Sugerencias contenedores
    function showDeptSuggestions(list) {
        if (!deptSuggestions) return;
        deptSuggestions.innerHTML = '';
        list.forEach(d => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'list-group-item list-group-item-action';
            btn.textContent = d.text;
            btn.dataset.value = d.value;
            deptSuggestions.appendChild(btn);
        });
        deptSuggestions.style.display = list.length ? 'block' : 'none';
    }

    function hideDeptSuggestions() {
        if (!deptSuggestions) return;
        deptSuggestions.style.display = 'none';
        deptSuggestions.innerHTML = '';
    }

    function showCitySuggestions(list) {
        if (!citySuggestions) return;
        citySuggestions.innerHTML = '';
        list.forEach(c => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'list-group-item list-group-item-action';
            btn.textContent = c.name + (c.dept ? ' — ' + c.dept : '');
            btn.dataset.cityId = c.id;
            btn.dataset.cityName = c.name;
            btn.dataset.dept = c.dept || '';
            citySuggestions.appendChild(btn);
        });
        citySuggestions.style.display = list.length ? 'block' : 'none';
    }

    function hideCitySuggestions() {
        if (!citySuggestions) return;
        citySuggestions.style.display = 'none';
        citySuggestions.innerHTML = '';
    }

    // Eventos: departamentoInput
    if (departamentoInput) {
        departamentoInput.addEventListener('focus', function () {
            showDeptSuggestions(deptOriginalOptions.slice(0,50));
        });

        departamentoInput.addEventListener('input', function () {
            const q = normalizeString(this.value || '');
            if (!q) { hideDeptSuggestions(); return; }
            const matches = deptOriginalOptions.filter(o => normalizeString(o.text).includes(q)).slice(0,50);
            showDeptSuggestions(matches);
        });

        departamentoInput.addEventListener('blur', function () {
            setTimeout(hideDeptSuggestions, 150);
        });

        // click en sugerencias
        if (deptSuggestions) {
            deptSuggestions.addEventListener('click', function (e) {
                const btn = e.target.closest('button');
                if (!btn) return;
                const val = btn.dataset.value;
                const text = btn.textContent;
                departamentoInput.value = text;
                if (deptSelect) {
                    deptSelect.value = val || text;
                    // disparar cambio
                    const ev = new Event('change');
                    deptSelect.dispatchEvent(ev);
                }
                hideDeptSuggestions();
            });
        }
    }

    // Cuando cambia el select real de departamento (p. ej. al enviar form o elegir sugerencia)
    if (deptSelect) {
        deptSelect.addEventListener('change', function () {
            const sel = this.value || this.options[this.selectedIndex].text;
            populateCitiesForDept(sel, '');
            if (ciudadInput) ciudadInput.value = '';
        });
    }

    // Eventos: ciudadInput
    if (ciudadInput) {
        ciudadInput.addEventListener('focus', function () {
            // mostrar ciudades actualmente cargadas
            if (currentCityOptions.length > 0) {
                const list = currentCityOptions.map(c => ({ id: c.id, name: c.name, dept: (deptSelect ? deptSelect.options[deptSelect.selectedIndex]?.text : '') }));
                showCitySuggestions(list.slice(0,50));
            } else {
                // mostrar primeras del catálogo global
                const all = Object.keys(CITY_MAP).reduce((acc, d) => {
                    (CITY_MAP[d] || []).slice(0,5).forEach(c => acc.push({ id: c.id, name: c.name, dept: d }));
                    return acc;
                }, []).slice(0,50);
                showCitySuggestions(all);
            }
        });

        ciudadInput.addEventListener('input', function () {
            const q = normalizeString(this.value || '');
            if (!q) { hideCitySuggestions(); return; }
            // buscar en lookup
            const candidates = [];
            Object.keys(CITY_MAP).forEach(dept => {
                (CITY_MAP[dept] || []).forEach(c => {
                    if (normalizeString(c.name).includes(q)) candidates.push({ id: c.id, name: c.name, dept: dept });
                });
            });
            candidates.sort((a,b)=>a.name.localeCompare(b.name,'es'));
            showCitySuggestions(candidates.slice(0,20));
        });

        ciudadInput.addEventListener('blur', function () { setTimeout(hideCitySuggestions, 150); });

        if (citySuggestions) {
            citySuggestions.addEventListener('click', function (e) {
                const btn = e.target.closest('button');
                if (!btn) return;
                const name = btn.dataset.cityName;
                const id = btn.dataset.cityId;
                const dept = btn.dataset.dept;
                ciudadInput.value = name;
                if (citySelect) citySelect.value = id;
                if (dept && departamentoInput) departamentoInput.value = dept;
                if (dept && deptSelect) {
                    // Intentar sincronizar el select de departamento y poblar ciudades
                    const match = Array.from(deptSelect.options).find(o => normalizeString(o.text) === normalizeString(dept));
                    if (match) {
                        // establecer el valor del select de departamento
                        deptSelect.value = match.value;
                        // poblar el select de ciudades y seleccionar la ciudad por id
                        try {
                            populateCitiesForDept(match.value || match.text, id);
                        } catch (err) {
                            // como fallback, disparar el evento change (antigua conducta)
                            deptSelect.dispatchEvent(new Event('change'));
                        }
                    } else {
                        // si no existe la opción en el select, simplemente poblar usando el nombre del dept
                        try { populateCitiesForDept(dept, id); } catch (e) {}
                    }
                }
                hideCitySuggestions();
            });
        }
    }

    // Inicialización: cargar JSON y poblar
    (async function init() {
        await loadCityJson();
        buildDeptOptionsFromMap();
        populateDeptDatalist();
        populateDeptSelect();
        // Si hay valor inicial en select, sincronizar input y poblar ciudades
        if (deptSelect && deptSelect.value) {
            const selectedText = deptSelect.options[deptSelect.selectedIndex].text;
            if (departamentoInput) departamentoInput.value = selectedText;
            populateCitiesForDept(deptSelect.value, document.querySelector('#initial_ciudad_id')?.value || '');
        }
        console.info('clientes.js inicializado. departamentos=', deptOriginalOptions.length);
    })();

});
