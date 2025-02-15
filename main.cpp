/** 
 * @file main.cpp
 * @brief A file that checks if a person is slouching and provides visual and 
 * audio warnings.
 */

// Include necessary libraries
#include <ctime>
#include <opencv2/opencv.hpp>
#include <SFML/Audio.hpp>

extern "C" {
    #include <cmath>

    /**
     * @brief Calculates the Euclidean distance between two points.
     * @param x1 The x-coordinate of the first point.
     * @param y1 The y-coordinate of the first point.
     * @param x2 The x-coordinate of the second point.
     * @param y2 The y-coordinate of the second point.
     * @return The Euclidean distance between the two points. Returns -1.0 if 
     * any of the parameters is NaN.
     */
    double calculate_distance(double x1, double y1, double x2, double y2) {
        if (std::isnan(x1) || std::isnan(y1) || std::isnan(x2) || std::isnan(y2)) {
            return -1.0; // Return an error value
        }
        return std::sqrt(std::pow(x2 - x1, 2) + std::pow(y2 - y1, 2));
    }

    /**
     * @brief Checks if a person is slouching.
     * @param distance The distance between two points on the person's body.
     * @param threshold The threshold distance for slouching.
     * @return True if the person is slouching (i.e., the distance is greater than 
     * the threshold), false otherwise.
     */
    bool is_slouching(double distance, double threshold) {
        return distance > threshold;
    }
}
int main() {
    double distance = 50.0, threshold = 40.0;
    std::time_t start_time = 0;
    cv::Mat image = cv::imread("path_to_your_image.jpg"); // Load an image using OpenCV

    // Initialize SFML SoundBuffer and Sound for playing the warning sound
    sf::SoundBuffer buffer;
    if (!buffer.loadFromFile("warning.wav")) {
        return -1; // error
    }
    sf::Sound warning_sound;
    warning_sound.setBuffer(buffer);

    // Check if the person is slouching
    if (distance > threshold) {
        if (start_time == 0) {
            start_time = std::time(nullptr); 
        } else if (std::time(nullptr) - start_time > 60) { // 1 minute
            // Draw a yellow border around the image
            cv::rectangle(
                image, 
                cv::Point(0, 0), 
                cv::Point(image.cols, image.rows), 
                cv::Scalar(0, 255, 255), 
                10
            );

            if (std::time(nullptr) - start_time > 120) { // 2 minutes
                // Play warning sound
                warning_sound.play();

                // Draw a red border around the image
                cv::rectangle(
                    image, 
                    cv::Point(0, 0), 
                    cv::Point(image.cols, image.rows), 
                    cv::Scalar(0, 0, 255), 
                    10
                );

                // Put text on the image
                cv::putText(
                    image, 
                    "Try to develop postural awareness", 
                    cv::Point(10, 60), 
                    cv::FONT_HERSHEY_SIMPLEX, 
                    1, 
                    cv::Scalar(0, 0, 255), 
                    2
                );
                cv::putText(
                    image, 
                    "Adjust your desk, chair and", 
                    cv::Point(10, 90), 
                    cv::FONT_HERSHEY_SIMPLEX, 
                    1, 
                    cv::Scalar(0, 0, 255), 
                    2
                );
                cv::putText(
                    image, 
                    "computer screen", 
                    cv::Point(10, 120), 
                    cv::FONT_HERSHEY_SIMPLEX, 
                    1, 
                    cv::Scalar(0, 0, 255), 
                    2
                );
            }
        }
    } else {
        start_time = 0;
        // Draw a green border around the image
        cv::rectangle(
            image, 
            cv::Point(0, 0), 
            cv::Point(image.cols, image.rows), 
            cv::Scalar(0, 255, 0), 
            10
        );
    }

    cv::imshow("Slouch Detection", image);
    cv::waitKey(0);
    return 0;
}
