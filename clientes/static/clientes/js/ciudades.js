// static/clientes/js/ciudades.js
(function() {
    const municipios = {
        'Amazonas': ['Leticia', 'Puerto Nariño', 'El Encanto', 'La Chorrera', 'La Pedrera', 'La Victoria', 'Mirití-Paraná', 'Puerto Alegría', 'Puerto Arica', 'Puerto Santander', 'Tarapacá'],
        'Antioquia': ['Medellín', 'Bello', 'Itagüí', 'Envigado', 'Rionegro', 'Apartadó', 'Turbo', 'Caucasia', 'Carmen de Viboral', 'Marinilla', 'La Estrella', 'Sabaneta', 'Caldas', 'Copacabana', 'Girardota', 'Barbosa', 'Santa Fe de Antioquia', 'Yarumal', 'Santa Rosa de Osos', 'Donmatías', 'Entrerríos', 'San Pedro de los Milagros', 'Guarne', 'El Retiro', 'La Ceja', 'El Santuario', 'Granada', 'San Luis', 'San Carlos', 'Puerto Berrío', 'Puerto Nare', 'Puerto Triunfo', 'Segovia', 'Remedios', 'Amalfi', 'Cisneros', 'Yolombó', 'Vegachí', 'Maceo', 'Caracolí', 'Santo Domingo', 'Concepción', 'Alejandría', 'San Roque', 'San Rafael'],
        'Arauca': ['Arauca', 'Tame', 'Saravena', 'Arauquita', 'Cravo Norte', 'Fortul', 'Puerto Rondón'],
        'Atlántico': ['Barranquilla', 'Soledad', 'Malambo', 'Puerto Colombia', 'Galapa', 'Sabanalarga', 'Santo Tomás', 'Palmar de Varela', 'Ponedera', 'Candelaria', 'Campo de la Cruz', 'Manatí', 'Suán', 'Luruaco', 'Repelón', 'Juan de Acosta', 'Tubará', 'Usiacurí', 'Baranoa', 'Polonuevo'],
        'Bolívar': ['Cartagena', 'Magangué', 'Turbaco', 'Arjona', 'El Carmen de Bolívar', 'San Pablo', 'Santa Rosa del Sur', 'Simití', 'Achí', 'Montecristo', 'Tiquisio', 'Río Viejo', 'Regidor', 'El Peñón', 'Hatillo de Loba', 'San Martín de Loba', 'Altos del Rosario', 'Barranco de Loba', 'Pinillos', 'Cicuco', 'Mompós', 'Talaigua Nuevo', 'Margarita', 'San Fernando', 'Calamar', 'Mahates', 'María La Baja', 'San Cristóbal', 'San Estanislao', 'Santa Catalina', 'Villanueva', 'San Jacinto', 'San Juan Nepomuceno', 'Córdoba', 'Zambrano', 'Clemencia', 'Santa Rosa', 'Norosí'],
        'Boyacá': ['Tunja', 'Duitama', 'Sogamoso', 'Chiquinquirá', 'Puerto Boyacá', 'Moniquirá', 'Ramiriquí', 'Ciénega', 'Samacá', 'Villa de Leyva', 'Paipa', 'Sotaquirá', 'Tuta', 'Tibasosa', 'Nobsa', 'Santa Rosa de Viterbo', 'Belén', 'Cerinza', 'Floresta', 'Betéitiva', 'Busbanzá', 'Corrales', 'Gámeza', 'Tópaga', 'Mongua', 'Monguí', 'Socotá', 'Socha', 'Paz de Río', 'Tasco', 'Jericó', 'Sativenorte', 'Sativásur', 'Chita', 'La Uvita', 'San Mateo', 'Bochica', 'Panqueba', 'Güicán', 'El Cocuy', 'Chiscas', 'El Espino', 'Guacamayas', 'San Juan de Giraldo', 'Cubará', 'Covarachía', 'Tipacoque', 'Soatá', 'Susacón', 'La Capilla', 'San Miguel de Sema', 'Raquirá', 'San Eduardo', 'Zetaquira', 'Berbeo', 'Pesca', 'Tota', 'Aquitania', 'Cuítiva', 'Iza', 'Firavitoba', 'Siachoque', 'Toca', 'Chivatá', 'Oicatá', 'Motavita', 'Cómbita', 'Arcabuco', 'Gachantivá', 'Sáchica', 'Cucaita', 'Ráquira', 'Guachetá', 'Lenguazaque', 'Susa', 'Simijaca', 'Calima', 'San José de Pare', 'Togüí', 'San Pablo de Borbur', 'Otanche', 'Pauna', 'Muzo', 'Quípama', 'Coper', 'Maripí', 'Buenavista', 'La Victoria', 'Briceño', 'Tununguá'],
        'Caldas': ['Manizales', 'Villamaría', 'Chinchiná', 'Palestina', 'Neira', 'Aranzazu', 'Salamina', 'Pácora', 'Aguadas', 'La Merced', 'Filadelfia', 'Marmato', 'Riosucio', 'Supía', 'Viterbo', 'San José', 'Anserma', 'Belalcázar', 'Risaralda', 'Manzanares', 'Marulanda', 'Samaná', 'Victoria', 'Norcasia', 'La Dorada'],
        'Caquetá': ['Florencia', 'San Vicente del Caguán', 'Puerto Rico', 'Cartagena del Chairá', 'Curillo', 'El Doncello', 'El Paujil', 'La Montañita', 'Milán', 'Morelia', 'Puerto Milán', 'Solano', 'Solita', 'Valparaíso', 'Albania'],
        'Casanare': ['Yopal', 'Aguazul', 'Villanueva', 'Tauramena', 'Monterrey', 'Nunchía', 'San Luis de Palenque', 'Trinidad', 'Pore', 'Paz de Ariporo', 'Hato Corozal', 'Maní', 'Orocué', 'Chámeza', 'Recetor', 'Sabanalarga', 'Sácama', 'La Salina'],
        'Cauca': ['Popayán', 'Santander de Quilichao', 'Puerto Tejada', 'Miranda', 'Corinto', 'Padilla', 'Guachené', 'Caloto', 'Villa Rica', 'Cajibío', 'El Tambo', 'Morales', 'Piendamó', 'Silvia', 'Jambaló', 'Toribío', 'Páez', 'Inzá', 'Timbío', 'Rosas', 'La Sierra', 'Almaguer', 'San Sebastián', 'Santa Rosa', 'La Vega', 'Bolívar', 'Mercaderes', 'Florencia', 'Argelia', 'Balboa', 'Patía', 'Sucre', 'Timbiquí', 'Guapi', 'López de Micay', 'Buenos Aires'],
        'Cesar': ['Valledupar', 'Aguachica', 'Bosconia', 'Codazzi', 'La Jagua de Ibirico', 'Chiriguaná', 'Curumaní', 'Pailitas', 'Pelaya', 'Tamalameque', 'Gamarra', 'González', 'Río de Oro', 'San Alberto', 'San Martín', 'Becerril', 'Manaure Balcón del Cesar', 'La Paz', 'San Diego', 'Urumita', 'Villanueva'],
        'Chocó': ['Quibdó', 'Istmina', 'Condoto', 'Carmen del Darién', 'Riosucio', 'Unguía', 'Acandí', 'Juradó', 'Bahía Solano', 'Nuquí', 'Bojayá', 'Medio Atrato', 'Lloró', 'Atrato', 'Río Quito', 'Bagadó', 'Cértegui', 'San José del Palmar', 'Novita', 'Sipí', 'Litoral del San Juan', 'El Cantón del San Pablo', 'Bajo Baudó', 'Medio Baudó', 'Alto Baudó'],
        'Córdoba': ['Montería', 'Cereté', 'Sahagún', 'Lorica', 'Ciénaga de Oro', 'San Pelayo', 'San Carlos', 'Planeta Rica', 'Buenavista', 'La Apartada', 'Montelíbano', 'Puerto Libertador', 'Ayapel', 'Pueblo Nuevo', 'Chinú', 'Sampués', 'San Andrés de Sotavento', 'Tuchín', 'Momil', 'Purísima', 'San Bernardo del Viento', 'Moñitos', 'Canalete', 'Los Córdobas', 'Puerto Escondido', 'Tierralta', 'Valencia'],
        'Cundinamarca': ['Bogotá', 'Soacha', 'Facatativá', 'Zipaquirá', 'Chía', 'Cajicá', 'Sopó', 'Tocancipá', 'Gachancipá', 'Madrid', 'Mosquera', 'Funza', 'Cota', 'Tenjo', 'Tabio', 'Subachoque', 'El Rosal', 'La Calera', 'Guasca', 'Sesquilé', 'Suesca', 'Nemocón', 'Cogua', 'Pacho', 'Villeta', 'Guaduas', 'Caparrapí', 'Puerto Salgar', 'La Palma', 'Yacopí', 'Topaipí', 'Villagómez', 'El Peñón', 'Vergara', 'Nocaima', 'Quebradanegra', 'San Francisco', 'Sasaima', 'Albán', 'Guayabal de Síquima', 'Vianí', 'Bituima', 'Anolaima', 'Apulo', 'Tocaima', 'Agua de Dios', 'Nilo', 'Ricaurte', 'Girardot', 'Flandes', 'Melgar', 'Carmen de Apicalá', 'Cunday', 'Icononzo', 'Villarrica', 'Arbeláez', 'Pandi', 'San Bernardo', 'Fusagasugá', 'Pasca', 'Silvania', 'Sibaté', 'Granada', 'San Antonio del Tequendama', 'Tena', 'La Mesa', 'Anapoima', 'Quipile', 'Jerusalén', 'Guataquí', 'Beltrán', 'Pulí', 'San Juan de Rioseco', 'Chaguaní'],
        'Guainía': ['Inírida', 'Barranco Minas', 'Cacahual', 'La Guadalupe', 'Mapiripana', 'Morichal', 'Pana Pana', 'Puerto Colombia', 'San Felipe'],
        'Guaviare': ['San José del Guaviare', 'Calamar', 'El Retorno', 'Miraflores'],
        'Huila': ['Neiva', 'Pitalito', 'Garzón', 'La Plata', 'Campoalegre', 'Rivera', 'Palermo', 'Santa María', 'Tello', 'Baraya', 'Villavieja', 'Aipe', 'Yaguará', 'Hobo', 'Algeciras', 'Gigante', 'Agrado', 'Altamira', 'Tarqui', 'Suaza', 'Guadalupe', 'Pital', 'Saladoblanco', 'Oporapa', 'Isnos', 'San Agustín', 'Timaná', 'Elías', 'Acevedo', 'Palestina'],
        'La Guajira': ['Riohacha', 'Maicao', 'Uribia', 'Manaure', 'San Juan del Cesar', 'Dibulla', 'Fonseca', 'Barrancas', 'Distracción', 'Hatonuevo', 'Albania', 'El Molino', 'La Jagua del Pilar', 'Urumita', 'Villanueva'],
        'Magdalena': ['Santa Marta', 'Ciénaga', 'Fundación', 'El Banco', 'Plato', 'Aracataca', 'Zona Bananera', 'Pivijay', 'Remolino', 'Salamina', 'Sitionuevo', 'Cerro de San Antonio', 'Concordia', 'Pedraza', 'Chibolo', 'Tenerife', 'San Zenón', 'Santa Ana', 'Pijiño del Carmen', 'San Sebastián de Buenavista', 'Sabanas de San Ángel', 'Ariguaní', 'Nueva Granada', 'El Piñón', 'Algarrobo', 'Santa Bárbara de Pinto'],
        'Meta': ['Villavicencio', 'Acacías', 'Granada', 'Puerto López', 'San Martín', 'Cumaral', 'Restrepo', 'Puerto Gaitán', 'Puerto Lleras', 'Puerto Rico', 'Mapiripán', 'Mesetas', 'La Macarena', 'Uribe', 'Lejanías', 'San Juan de Arama', 'Vista Hermosa', 'Castilla la Nueva', 'San Carlos de Guaroa', 'El Dorado', 'Barranca de Upía', 'Cabuyaro', 'Fuente de Oro'],
        'Nariño': ['Pasto', 'Ipiales', 'Tumaco', 'Túquerres', 'La Unión', 'Buesaco', 'Chachagüí', 'Yacuanquer', 'Funes', 'Imués', 'Ospina', 'Guaitarilla', 'Tangua', 'Sandoná', 'Consacá', 'Ancuya', 'Linares', 'Samaniego', 'Providencia', 'Santacruz', 'Puerres', 'Córdoba', 'Potosí', 'Gualmatán', 'El Peñol', 'Contadero', 'Iles', 'San Pablo', 'La Cruz', 'San Bernardo', 'Belén', 'San Pedro de Cartago', 'Colón', 'El Tablón de Gómez', 'La Florida', 'Nariño', 'Albán', 'Arboleda', 'San Lorenzo', 'Taminango', 'El Rosario', 'Leiva', 'Policarpa', 'Cumbitara', 'Los Andes', 'La Llanada', 'Mallama', 'Cumbal', 'Guachucal', 'Aldana', 'Cuaspud', 'Carlosama', 'Ricaurte', 'Magüí', 'Barbacoas', 'Roberto Payán', 'Mosquera', 'Olaya Herrera', 'El Charco', 'La Tola', 'Santa Bárbara', 'Francisco Pizarro'],
        'Norte de Santander': ['Cúcuta', 'Ocaña', 'Pamplona', 'Los Patios', 'Villa del Rosario', 'El Zulia', 'San Cayetano', 'Santiago', 'Puerto Santander', 'Tibú', 'Sardinata', 'Ábrego', 'La Playa', 'Hacarí', 'San Calixto', 'Teorama', 'Convención', 'El Carmen', 'Tarso', 'Bucarasica', 'Salazar', 'Arboledas', 'Cáchira', 'La Esperanza', 'Chinácota', 'Ragonvalia', 'Herrán', 'Toledo', 'Labateca', 'Pamplonita', 'Mutiscua', 'Silos', 'Cácota', 'Chitagá', 'Cucutilla', 'Bochalema', 'Durania'],
        'Putumayo': ['Mocoa', 'Puerto Asís', 'Orito', 'Villagarzón', 'Sibundoy', 'San Francisco', 'Santiago', 'Colón', 'Valle del Guamuez', 'San Miguel', 'Puerto Caicedo', 'Puerto Guzmán', 'Leguízamo'],
        'Quindío': ['Armenia', 'Calarcá', 'Montenegro', 'Quimbaya', 'La Tebaida', 'Circasia', 'Filandia', 'Salento', 'Buenavista', 'Pijao', 'Córdoba', 'Génova'],
        'Risaralda': ['Pereira', 'Dosquebradas', 'Santa Rosa de Cabal', 'La Virginia', 'Apía', 'Balboa', 'Belén de Umbría', 'Guática', 'La Celia', 'La Merced', 'Marsella', 'Mistrató', 'Pueblo Rico', 'Quinchía', 'Santuario'],
        'San Andrés y Providencia': ['San Andrés', 'Providencia'],
        'Santander': ['Bucaramanga', 'Floridablanca', 'Girón', 'Piedecuesta', 'Barrancabermeja', 'San Gil', 'Socorro', 'Vélez', 'Málaga', 'Barbosa', 'Puerto Wilches', 'Sabana de Torres', 'Rionegro', 'Lebrija', 'Los Santos', 'Zapatoca', 'Betulia', 'San Vicente de Chucurí', 'El Carmen de Chucurí', 'Simacota', 'Palmar', 'Oiba', 'Guadalupe', 'Suaita', 'Contratación', 'Santa Helena del Opón', 'La Paz', 'Chipatá', 'Güepsa', 'San Benito', 'Aguada', 'San José de Miranda', 'Capitanejo', 'Macaravita', 'Carcasí', 'Enciso', 'Concepción', 'San Andrés', 'Guaca', 'Molagavita', 'San Miguel', 'Cerrito', 'Aratoca', 'Curití', 'Villanueva', 'Barichara', 'Galán', 'Hato', 'Palmas del Socorro', 'Confines', 'Chima', 'Jordán', 'Ocamonte', 'Valle de San José', 'Onzaga', 'Coromoro', 'Charalá', 'Encino', 'Gámbita', 'Sucre', 'Bolívar', 'El Peñón', 'Cimitarra', 'Landázuri', 'Puerto Parra', 'El Guacamayo', 'Santa Bárbara', 'Florián', 'Albania', 'Jesús María', 'La Belleza', 'Guavatá', 'Puente Nacional', 'San José de Pare', 'Toguí', 'Moniquirá'],
        'Sucre': ['Sincelejo', 'Corozal', 'Sampués', 'San Antonio de Palmito', 'San Onofre', 'Santiago de Tolú', 'Coveñas', 'San Luis de Sincé', 'San Benito Abad', 'La Unión', 'San Marcos', 'Majagual', 'Sucre', 'Guaranda', 'Caimito', 'Chalán', 'Colosó', 'Morroa', 'Ovejas', 'Los Palmitos', 'Galeras', 'Buenavista', 'San Pedro', 'Palmito', 'San Juan de Betulia'],
        'Tolima': ['Ibagué', 'Espinal', 'Melgar', 'Líbano', 'Honda', 'Mariquita', 'Fresno', 'Méndez', 'San Sebastián de Mariquita', 'Armero', 'Falan', 'Palocabildo', 'Casabianca', 'Villahermosa', 'Anzoátegui', 'Santa Isabel', 'Venadillo', 'Alvarado', 'Piedras', 'Coello', 'Guamo', 'Saldaña', 'Purificación', 'Prado', 'Dolores', 'Cunday', 'Villarrica', 'Ortega', 'Chaparral', 'Rioblanco', 'Planadas', 'Ataco', 'Natagaima', 'Coyaima', 'Rovira', 'San Antonio', 'Roncesvalles', 'San Luis', 'Valle de San Juan', 'Cajamarca', 'Anaime'],
        'Valle del Cauca': ['Cali', 'Palmira', 'Buenaventura', 'Tuluá', 'Cartago', 'Buga', 'Jamundí', 'Yumbo', 'Florida', 'Pradera', 'Candelaria', 'El Cerrito', 'Ginebra', 'Guacarí', 'Restrepo', 'Dagua', 'La Cumbre', 'Vijes', 'Yotoco', 'Calima', 'Riofrío', 'Trujillo', 'Bolívar', 'Zarzal', 'La Victoria', 'La Unión', 'Roldanillo', 'Tororo', 'Argelia', 'El Dovio', 'Versalles', 'Sevilla', 'Caicedonia', 'Alcalá', 'Ulloa', 'Ansermanuevo', 'El Águila', 'El Cairo', 'Obando'],
        'Vaupés': ['Mitú', 'Carurú', 'Pacoa', 'Papunahua', 'Taraira', 'Yavaraté'],
        'Vichada': ['Puerto Carreño', 'La Primavera', 'Santa Rosalía', 'Cumaribo']
    };

    document.addEventListener('DOMContentLoaded', function() {
        const departamento = document.getElementById('id_departamento');
        const ciudadSelect = document.getElementById('id_ciudad');
        const ciudadHidden = document.getElementById('id_ciudad_original');

        if (!departamento || !ciudadSelect) return;

        function cargarMunicipios() {
            const depto = departamento.value;
            const ciudades = municipios[depto] || [];

            ciudadSelect.innerHTML = '';

            if (!depto) {
                ciudadSelect.innerHTML = '<option value="">Primero seleccione un departamento</option>';
                ciudadSelect.disabled = true;
                return;
            }

            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.textContent = 'Seleccione un municipio';
            ciudadSelect.appendChild(defaultOption);

            ciudades.sort().forEach(m => {
                const option = document.createElement('option');
                option.value = m;
                option.textContent = m;
                ciudadSelect.appendChild(option);
            });

            ciudadSelect.disabled = false;

            if (ciudadHidden && ciudadHidden.value) {
                ciudadSelect.value = ciudadHidden.value;
            }
        }

        function sincronizarCampoOculto() {
            if (ciudadHidden) {
                ciudadHidden.value = ciudadSelect.value;
            }
        }

        departamento.addEventListener('change', cargarMunicipios);
        ciudadSelect.addEventListener('change', sincronizarCampoOculto);

        const form = document.querySelector('form');
        if (form) {
            form.addEventListener('submit', sincronizarCampoOculto);
        }

        if (departamento.value) {
            cargarMunicipios();
        }
    });
})();