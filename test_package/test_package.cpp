#include <cstdlib>
#include <iostream>
#include <SFML/System.hpp>
#include <SFML/Window.hpp>
#include <SFML/Graphics.hpp>
#include <SFML/Audio.hpp>
#include <SFML/Network.hpp>

int main()
{
    // Test System
    sf::Clock clock;
    const sf::Time duration = clock.getElapsedTime();
    std::cout << "Elapsed Time: " << duration.asMicroseconds() << " microseconds\n";

    // Test Window & Graphics
    sf::RenderWindow window(sf::VideoMode(1200, 800), "Test");

    // Test Audio
    sf::SoundBuffer soundBuffer;
    soundBuffer.loadFromFile("dummy");

    // Test Network
    sf::TcpListener listener;
    listener.listen(53000);

    return EXIT_SUCCESS;
}
