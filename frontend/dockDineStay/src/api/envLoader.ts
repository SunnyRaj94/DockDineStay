import dotenv from 'dotenv';
import fs from 'fs';
import path from 'path';

interface EnvVars {
  [key: string]: string | undefined;
}

const loadEnv = (fileDir: string, fileName: string = '.env'): EnvVars | undefined => {
  const envVars: EnvVars = {};
  const envPath = path.join(fileDir, fileName);
  const envFileDir = process.env.ENV_FILE_DIR;

  if (fs.existsSync(envPath)) {
    const envConfig = dotenv.parse(fs.readFileSync(envPath));
    return envConfig;
  } else if (envFileDir && fs.existsSync(path.join(envFileDir, fileName))) {
    const envConfig = dotenv.parse(fs.readFileSync(path.join(envFileDir, fileName)));
    return envConfig;
  } else {
    const keys = Object.keys(process.env).filter((k) => k.startsWith('ENV_VAR'));
    if (keys.length) {
      keys.forEach((key) => {
        envVars[key.replace('ENV_VAR', '')] = process.env[key];
      });
      return envVars;
    }
  }

  return undefined;
};

// Auto-run and export
const loadedEnv = loadEnv(__dirname);
export default loadedEnv;
