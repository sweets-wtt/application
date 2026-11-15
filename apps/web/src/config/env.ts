/** API 基地址：未注入时走同源相对路径 */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

export default API_BASE_URL;
