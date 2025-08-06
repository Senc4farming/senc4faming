package com.example.senc4farming.webapp;

import com.example.senc4farming.Senc4farmingApplication;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;

@SpringBootTest
class webappTests {

	@Test
	void contextLoads() {
   // Creado por Spring Boot para verificar que el contexto de la aplicación se carga correctamente.
 }
	
    @Test
    void testMainMethod() {
        assertDoesNotThrow(() -> {
            Senc4farmingApplication.main(new String[]{});
        }, "El método main no debería lanzar excepciones");
    }

}
