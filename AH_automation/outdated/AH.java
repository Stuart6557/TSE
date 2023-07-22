/**
 * This file was created to help me hunt down people who didn't 
 * fill out the AH Response form after AH. 
 * 
 * It asks you to paste the names from the roster and the names 
 * from the AH Response form. It first outputs the names in the  
 * roster but not in the AH Response form, then the names in 
 * the AH Response form but not in the roster.
 * 
 * I wrote this in a few minutes during the school year to make 
 * my life easier, but then I decided that it didn't make my 
 * life easy enough. I still had to manually check everyone's 
 * graduation dates, which was super boring and time consuming 
 * since TSE has around 90 members. Also, a lot of the names 
 * in the roster didn't match up with the names in the AH 
 * Response form (for example, if someone's name was "Joseph 
 * John-Doe" on the roster, that person may write "Joe John-
 * Doe" or "Joseph John" or something like that in the AH 
 * Response form), which made both outputted lists very long 
 * and very tedious to go through manually.
 * 
 * I decided to abandon this file to write some code that 
 * addressed both of these pain points.
 */

import java.util.*;
import java.io.*;

class AH {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);
        Set<String> roster = new HashSet<>();
        Set<String> AH = new HashSet<>();

        System.out.println("roster names:");
        String name = input.nextLine().trim().toLowerCase();
        while (!name.equals("")) {
            roster.add(name);
            name = input.nextLine().trim().toLowerCase();
        }

        System.out.println("AH names:");
        name = input.nextLine().trim().toLowerCase();
        while (!name.equals("")) {
            if(roster.contains(name)) {
                roster.remove(name);
            } else {
                AH.add(name);
            }
            name = input.nextLine().trim().toLowerCase();
        }

        try {
            // File out = new File("AH.txt");
            FileWriter writer = new FileWriter("AH.txt");

            writer.write("Names in roster but not in AH\n");
            for (String person : roster) {
                writer.write(person + "\n");
            }

            writer.append("\nNames in AH but not in roster\n");
            for (String person : AH) {
                writer.write(person + "\n");
            }

            writer.close();
        } catch (IOException e) {
            System.out.println("error");
            e.printStackTrace();
        }

        input.close();
    }
}