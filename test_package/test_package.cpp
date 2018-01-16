#include <cstdlib>
#include <iostream>
#include <SFML/System.hpp>
#include <SFML/Graphics.hpp>
#include <SFML/Audio.hpp>

int main()
{
    // Test System
    sf::Clock clock{};
    const auto duration = clock.getElapsedTime();
    std::cout << "Elapsed Time: " << duration.asMicroseconds() << " microseconds\n";

    // Test Graphics
    sf::RenderWindow window{ { 1200, 800 }, "Test" };

    // Test Audio
    sf::SoundBuffer soundBuffer{};
    soundBuffer.loadFromFile("dummy");

    return EXIT_SUCCESS;
}
