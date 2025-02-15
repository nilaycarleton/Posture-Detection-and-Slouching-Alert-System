#include <cmath>
#include <iostream>
#include <opencv2/opencv.hpp>
#include <SFML/Audio.hpp>

extern "C" {

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
