interface EnvVars {
  API_BASE_URL: string;
  // Add other environment variables you need
}

const envVars: EnvVars = {
  API_BASE_URL: "https://dockdinestay-apiservice.onrender.com",
};

console.log("Environment variables loaded:", envVars);

export default envVars;
