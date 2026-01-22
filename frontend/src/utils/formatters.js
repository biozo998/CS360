/**
 * Converte horas decimais (ex: 16.25) para formato horário (16:15)
 * @param {number|string} valor - O valor decimal das horas
 * @returns {string} - Horas formatadas HH:MM
 */
export const formatarHoraDecimal = (valor) => {
    if (valor === null || valor === undefined || valor === '') return '00:00';
    
    const numero = Number(valor);
    const negativo = numero < 0; // Guarda se é negativo para saldo
    const absoluto = Math.abs(numero);

    const horas = Math.floor(absoluto);
    const minutosDecimal = (absoluto - horas) * 60;
    
    // Arredonda os minutos para evitar 15.99999
    let minutos = Math.round(minutosDecimal);
    
    // Caso o arredondamento jogue 59.9 para 60, somamos 1 hora
    let horasFinais = horas;
    if (minutos === 60) {
        minutos = 0;
        horasFinais += 1;
    }

    // PadStart garante o zero à esquerda (ex: 5 vira 05)
    const horasString = String(horasFinais).padStart(2, '0');
    const minutosString = String(minutos).padStart(2, '0');

    return `${negativo ? '-' : ''}${horasString}:${minutosString}`;
};

// Aproveitamos para mover a formatação de data para cá também (Centralização)
export const formatarDataBR = (valor) => {
    if (!valor) return '-';
    // Adiciona o timezone UTC para evitar problemas de fuso horário (-3h)
    const data = new Date(valor);
    return data.toLocaleDateString('pt-BR', { timeZone: 'UTC' });
};