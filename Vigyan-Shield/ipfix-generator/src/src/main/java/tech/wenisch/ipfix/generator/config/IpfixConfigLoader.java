package tech.wenisch.ipfix.generator.config;

import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.FileNotFoundException;
import tech.wenisch.ipfix.generator.managers.IPFIXGeneratorManager;

public class IpfixConfigLoader {
    public static IpfixConfig loadConfig(String filePath) throws IOException {
        ObjectMapper objectMapper = new ObjectMapper();
        return objectMapper.readValue(new File(filePath), IpfixConfig.class);
    }
    public static IpfixConfig loadConfigFromClasspath(String resourceName) throws IOException {
    InputStream is = IPFIXGeneratorManager.class.getClassLoader().getResourceAsStream(resourceName);
    if (is == null) {
        throw new FileNotFoundException(resourceName + " not found in classpath");
    }
    ObjectMapper mapper = new ObjectMapper();
    return mapper.readValue(is, IpfixConfig.class);
}
}