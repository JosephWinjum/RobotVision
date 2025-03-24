/*
 *Hunter Lloyd
 * Copyrite.......I wrote, ask permission if you want to use it outside of class. 
 */

import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.io.File;
import java.awt.image.PixelGrabber;
import java.awt.image.MemoryImageSource;
import java.util.prefs.Preferences;

class IMP implements MouseListener{
   JFrame frame;
   JPanel mp;
   JButton start;
   JScrollPane scroll;
   JMenuItem openItem, exitItem, resetItem;
   Toolkit toolkit;
   File pic;
   ImageIcon img;
   int colorX, colorY;
   int [] pixels;
   int [] results;
   //Instance Fields you will be using below

   //This will be your height and width of your 2d array
   int height=0, width=0;

   //your 2D array of pixels
    int picture[][];

    /*
     * In the Constructor I set up the GUI, the frame the menus. The open pulldown
     * menu is how you will open an image to manipulate.
     */
   IMP()
   {
      toolkit = Toolkit.getDefaultToolkit();
      frame = new JFrame("Image Processing Software by Hunter");
      JMenuBar bar = new JMenuBar();
      JMenu file = new JMenu("File");
      JMenu functions = getFunctions();
      frame.addWindowListener(new WindowAdapter(){
            @Override
              public void windowClosing(WindowEvent ev){quit();}
            });
      openItem = new JMenuItem("Open");
      openItem.addActionListener(new ActionListener(){
            @Override
          public void actionPerformed(ActionEvent evt){ handleOpen(); }
           });
      resetItem = new JMenuItem("Reset");
      resetItem.addActionListener(new ActionListener(){
            @Override
          public void actionPerformed(ActionEvent evt){ reset(); }
           });
      exitItem = new JMenuItem("Exit");
      exitItem.addActionListener(new ActionListener(){
            @Override
          public void actionPerformed(ActionEvent evt){ quit(); }
           });
      file.add(openItem);
      file.add(resetItem);
      file.add(exitItem);
      bar.add(file);
      bar.add(functions);
      frame.setSize(600, 600);
      mp = new JPanel();
      mp.setBackground(new Color(0, 0, 0));
      scroll = new JScrollPane(mp);
      frame.getContentPane().add(scroll, BorderLayout.CENTER);
      JPanel butPanel = new JPanel();
      butPanel.setBackground(Color.black);
      start = new JButton("start");
      start.setEnabled(false);
      start.addActionListener(new ActionListener(){
            @Override
          public void actionPerformed(ActionEvent evt){ fun1(); }
           });
      butPanel.add(start);
      frame.getContentPane().add(butPanel, BorderLayout.SOUTH);
      frame.setJMenuBar(bar);
      frame.setVisible(true);
   }

   /*
    * This method creates the pulldown menu and sets up listeners to selection of the menu choices. If the listeners are activated they call the methods
    * for handling the choice, fun1, fun2, fun3, fun4, etc. etc.
    */

  private JMenu getFunctions() {
      JMenu fun = new JMenu("Functions");

      JMenuItem firstItem = new JMenuItem("MyExample - fun1 method");
      JMenuItem secondItem = new JMenuItem("Rotate 90");
      JMenuItem thirdItem = new JMenuItem("grayscale");
      JMenuItem fourthItem = new JMenuItem("blur");
      JMenuItem fifthItem = new JMenuItem("edge detection 5x5");
      JMenuItem sixthItem = new JMenuItem("edge detection 3x3");
      JMenuItem seventhItem = new JMenuItem("histogram");
      JMenuItem eigthItem = new JMenuItem("equalize");

      firstItem.addActionListener(new ActionListener() {
          @Override
          public void actionPerformed(ActionEvent evt) {
              fun1();
          }
      });
      secondItem.addActionListener(new ActionListener() {
          @Override
          public void actionPerformed(ActionEvent evt) {
              rotate90();
          }
      });
      thirdItem.addActionListener(new ActionListener() {
          @Override
          public void actionPerformed(ActionEvent evt) {
              grayscale();
          }
      });
      fourthItem.addActionListener(new ActionListener() {
          @Override
          public void actionPerformed(ActionEvent evt) {
              blur();
          }
      });
      fifthItem.addActionListener(new ActionListener() {
          @Override
          public void actionPerformed(ActionEvent evt) {
              edgeDetection5x5();
          }
      });
      sixthItem.addActionListener(new ActionListener() {
          @Override
          public void actionPerformed(ActionEvent evt) {
              edgeDetection3x3();
          }
      });
      seventhItem.addActionListener(new ActionListener() {
          @Override
          public void actionPerformed(ActionEvent evt) {
              histogram();
          }
      });
      eigthItem.addActionListener(new ActionListener() {
          @Override
          public void actionPerformed(ActionEvent evt) {
              equalize();
          }
      });


      fun.add(firstItem);
      fun.add(secondItem);
      fun.add(thirdItem);
      fun.add(fourthItem);
      fun.add(fifthItem);
      //fun.add(sixthItem);
      fun.add(seventhItem);
      fun.add(eigthItem);
      return fun;
  }


  /*
   * This method handles opening an image file, breaking down the picture to a one-dimensional array and then drawing the image on the frame.
   * You don't need to worry about this method.
   */
    private void handleOpen()
  {
     img = new ImageIcon();
     JFileChooser chooser = new JFileChooser();
      Preferences pref = Preferences.userNodeForPackage(IMP.class);
      String path = pref.get("DEFAULT_PATH", "");

      chooser.setCurrentDirectory(new File(path));
     int option = chooser.showOpenDialog(frame);

     if(option == JFileChooser.APPROVE_OPTION) {
        pic = chooser.getSelectedFile();
        pref.put("DEFAULT_PATH", pic.getAbsolutePath());
       img = new ImageIcon(pic.getPath());
      }
     width = img.getIconWidth();
     height = img.getIconHeight();

     JLabel label = new JLabel(img);
     label.addMouseListener(this);
     pixels = new int[width*height];

     results = new int[width*height];


     Image image = img.getImage();

     PixelGrabber pg = new PixelGrabber(image, 0, 0, width, height, pixels, 0, width );
     try{
         pg.grabPixels();
     }catch(InterruptedException e)
       {
          System.err.println("Interrupted waiting for pixels");
          return;
       }
     for(int i = 0; i<width*height; i++)
        results[i] = pixels[i];
     turnTwoDimensional();
     mp.removeAll();
     mp.add(label);

     mp.revalidate();
  }

  /*
   * The libraries in Java give a one dimensional array of RGB values for an image, I thought a 2-Dimensional array would be more usefull to you
   * So this method changes the one dimensional array to a two-dimensional.
   */
  private void turnTwoDimensional()
  {
     picture = new int[height][width];
     for(int i=0; i<height; i++)
       for(int j=0; j<width; j++)
          picture[i][j] = pixels[i*width+j];


  }
  /*
   *  This method takes the picture back to the original picture
   */
  private void reset()
  {
        for(int i = 0; i<width*height; i++)
             pixels[i] = results[i];
       Image img2 = toolkit.createImage(new MemoryImageSource(width, height, pixels, 0, width));

      JLabel label2 = new JLabel(new ImageIcon(img2));
       mp.removeAll();
       mp.add(label2);

       mp.revalidate();
    }
  /*
   * This method is called to redraw the screen with the new image.
   */
  private void resetPicture()
  {
       for(int i=0; i<height; i++)
       for(int j=0; j<width; j++)
          pixels[i*width+j] = picture[i][j];
      Image img2 = toolkit.createImage(new MemoryImageSource(width, height, pixels, 0, width));

      JLabel label2 = new JLabel(new ImageIcon(img2));
       mp.removeAll();
       mp.add(label2);

       mp.revalidate();

    }
    /*
     * This method takes a single integer value and breaks it down doing bit manipulation to 4 individual int values for A, R, G, and B values
     */
  private int [] getPixelArray(int pixel)
  {
      int temp[] = new int[4];
      temp[0] = (pixel >> 24) & 0xff;
      temp[1]   = (pixel >> 16) & 0xff;
      temp[2] = (pixel >>  8) & 0xff;
      temp[3]  = (pixel      ) & 0xff;
      return temp;

    }
    /*
     * This method takes an array of size 4 and combines the first 8 bits of each to create one integer.
     */
  private int getPixels(int rgb[])
  {
         int alpha = 0;
         int rgba = (rgb[0] << 24) | (rgb[1] <<16) | (rgb[2] << 8) | rgb[3];
        return rgba;
  }

  public void getValue()
  {
      int pix = picture[colorY][colorX];
      int temp[] = getPixelArray(pix);
      System.out.println("Color value " + temp[0] + " " + temp[1] + " "+ temp[2] + " " + temp[3]);
    }

  /**************************************************************************************************
   * This is where you will put your methods. Every method below is called when the corresponding pulldown menu is
   * used. As long as you have a picture open first the when your fun1, fun2, fun....etc method is called you will
   * have a 2D array called picture that is holding each pixel from your picture.
   *************************************************************************************************/
   /*
    * Example function that just removes all red values from the picture.
    * Each pixel value in picture[i][j] holds an integer value. You need to send that pixel to getPixelArray the method which will return a 4 element array
    * that holds A,R,G,B values. Ignore [0], that's the Alpha channel which is transparency, we won't be using that, but you can on your own.
    * getPixelArray will breaks down your single int to 4 ints so you can manipulate the values for each level of R, G, B.
    * After you make changes and do your calculations to your pixel values the getPixels method will put the 4 values in your ARGB array back into a single
    * integer value so you can give it back to the program and display the new picture.
    */
  private void fun1()
  {
      //traverse pixels
      for(int i=0; i<height; i++)
          for(int j=0; j<width; j++)
          {
              //stores alpha, red, green, blue
              int rgbArray[] = new int[4];

              //get three ints for Alpha, R, G and B
              rgbArray = getPixelArray(picture[i][j]);

              //sets 2nd spot in array to 0 (which is red, gets rid of reds)
              rgbArray[1] = 0;
              //puts the edited pixels back into the picture
              picture[i][j] = getPixels(rgbArray);
          }
      resetPicture();
  }

    private void rotate90() {
        //height is now width, width is now height
        int newHeight = width;
        int newWidth = height;

        int[][] rotated90Picture = new int[newHeight][newWidth];

        //was getting leftover parts of the image when rotating, filling with black in initial rotated image
        //fix later, still doesn't fix after images
        for (int i = 0; i < width; i++) {
            for (int j = 0; j < height; j++) {
                //make black so no after images leftover
                rotated90Picture[i][j] = 0xFF000000;
            }
        }
        resetPicture();

        for (int i = 0; i < newHeight; i++) {
            for (int j = 0; j < newWidth; j++) {
                //basically swap the old height/widths with the new ones
                //-1-j bc last row = new first column
                rotated90Picture[i][j] = picture[height - 1 - j][i];
            }
        }

        //make picture use the new 2d array, and adjust height/width values and reset
        picture = rotated90Picture;
        height = newHeight;
        width = newWidth;

        resetPicture();
    }


    private void grayscale() {
      for (int x = 0; x < height; x++) {
          for (int y = 0; y < width; y++) {
              //store rgb values of pixel
              int[] rgb = getPixelArray(picture[x][y]);
              int red = rgb[1];
              int green = rgb[2];
              int blue = rgb[3];
              //luminosity calcuation
              int gray = (int)(0.21*red + 0.72*green + 0.07*blue);
              //convert to grayscale
              rgb[1] = gray;
              rgb[2] = gray;
              rgb[3] = gray;
              picture[x][y] = getPixels(rgb);
          }
      }
      resetPicture();
    }

    private void blur() {
        grayscale();

        int[][] temp = new int[height][width];
        for (int i = 0; i < height; i++) {
            for (int j = 0; j < width; j++) {
                int sum = 0;
                int count = 0;
                for (int x = -1; x <= 1; x++) {
                    for (int y = -1; y <= 1; y++) {
                        int z1 = i + x;
                        int z2 = j + y;
                        if (z1 >= 0 && z1 < height && z2 >= 0 && z2 < width) {
                            int[] neighborRGB = getPixelArray(picture[z1][z2]);
                            sum += neighborRGB[1];
                            count++;
                        }
                    }
                }
                int avg = sum / count;
                int[] newRGB = {255, avg, avg, avg};
                temp[i][j] = getPixels(newRGB);
            }
        }
        picture = temp;
        resetPicture();
    }

    private void edgeDetection5x5() {
        //also need to check both this and 3x3, bc picture doesn't reset correctly between runs
        grayscale();

        int[][] kernel = {
                {-1, -1, -1, -1, -1},
                {-1,  0,  0,  0, -1},
                {-1,  0,  16,  0, -1},
                {-1,  0,  0,  0, -1},
                {-1, -1, -1, -1, -1}
        };

        int[][] temp = new int[height][width];

        for (int i = 0; i < height; i++) {
            for (int j = 0; j < width; j++) {
                int sum = 0;

                for (int x = 0; x < 5; x++) {
                    for (int y = 0; y < 5; y++) {
                        //have to offset
                        int row = i + (x - 2);
                        int col = j + (y - 2);

                        //make sure we don't exceed confinemetn
                        if (row >= 0 && row < height && col >= 0 && col < width) {
                            int[] rgb = getPixelArray(picture[row][col]);
                            int grayVal = rgb[1];
                            sum += grayVal * kernel[x][y];
                        }
                    }
                }
                if (sum < 0) sum = 0;
                if (sum > 255) sum = 255;
                int[] newRGB = {255, sum, sum, sum};
                temp[i][j] = getPixels(newRGB);
            }
        }

        picture = temp;
        resetPicture();
    }

    private void edgeDetection3x3() {
        grayscale();

        int[][] kernel = {
                {-1, -1, -1},
                {-1, 8, -1},
                {-1, -1, -1}
        };

        int[][] temp = new int[height][width];

        for (int i = 0; i < height; i++) {
            for (int j = 0; j < width; j++) {
                int sum = 0;

                for (int x = 0; x < 3; x++) {
                    for (int y = 0; y < 3; y++) {
                        //have to offset
                        int row = i + (x - 2);
                        int col = j + (y - 2);

                        //make sure we don't exceed confinemetn
                        if (row >= 0 && row < height && col >= 0 && col < width) {
                            int[] rgb = getPixelArray(picture[row][col]);
                            int grayVal = rgb[1];
                            sum += grayVal * kernel[x][y];
                        }
                    }
                }
                if (sum < 0) sum = 0;
                if (sum > 255) sum = 255;
                int[] newRGB = {255, sum, sum, sum};
                temp[i][j] = getPixels(newRGB);
            }
        }

        picture = temp;
        resetPicture();
    }


    private void histogram() {
        //hists for each eype
        int[] histR = new int[256];
        int[] histG = new int[256];
        int[] histB = new int[256];

        for(int i = 0; i < height; i++) {
            for(int j = 0; j < width; j++) {
                int[] rgb = getPixelArray(picture[i][j]);
                histR[rgb[1]]++;
                histG[rgb[2]]++;
                histB[rgb[3]]++;
            }
        }

        //3 frames ea color
        JFrame redFrame   = new JFrame("Red histogram");
        JFrame greenFrame = new JFrame("Green histogram");
        JFrame blueFrame  = new JFrame("Blue histogram");

        redFrame.setSize(300, 500);
        greenFrame.setSize(300, 500);
        blueFrame.setSize(300, 500);
        //sick of having to move these
        redFrame.setLocation(700, 100);
        greenFrame.setLocation(1050, 100);
        blueFrame.setLocation(1400, 100);
        redFrame.add(new SingleColorHistPanel(histR, Color.RED));
        greenFrame.add(new SingleColorHistPanel(histG, Color.GREEN));
        blueFrame.add(new SingleColorHistPanel(histB, Color.BLUE));

        //turn on
        redFrame.setVisible(true);
        greenFrame.setVisible(true);
        blueFrame.setVisible(true);

        resetPicture();
    }

    class SingleColorHistPanel extends JPanel {
        private int[] hist;
        //max of counts
        private int max;
        private Color color;

        public SingleColorHistPanel(int[] hist, Color color) {
            this.hist = hist;
            this.color = color;

            //scale those values for each hist
            for (int i = 0; i < hist.length; i++) {
                if (hist[i] > max) {
                    max = hist[i];
                }
            }
        }

        @Override
        protected void paintComponent(Graphics g) {
            super.paintComponent(g);

            int w = getWidth();
            int h = getHeight();

            //make sure all showing
            int barWidth = Math.max(1, w / 256);

            g.setColor(color);

            for (int i = 0; i < 256; i++) {
                //also make sure manageably sized
                double ratio = (double) hist[i] / max;
                int barHeight = (int) (ratio * h);

                int x = i * barWidth;
                int y = h - barHeight;
                g.fillRect(x, y, barWidth, barHeight);
            }
        }
    }


    private void equalize() {
        //need to rewrite this later, sometimes bugs out and i
        //think makes hist return incorrectly

        //get the hists and set them
        int[] histR = new int[256];
        int[] histG = new int[256];
        int[] histB = new int[256];

        for (int i = 0; i < height; i++) {
            for (int j = 0; j < width; j++) {
                int[] rgb = getPixelArray(picture[i][j]);
                histR[rgb[1]]++;
                histG[rgb[2]]++;
                histB[rgb[3]]++;
            }
        }

        int totalPixels = width * height;

        float[] cdfR = new float[256];
        float[] cdfG = new float[256];
        float[] cdfB = new float[256];
        //cum dist func to equalize
        cdfR[0] = histR[0];
        cdfG[0] = histG[0];
        cdfB[0] = histB[0];
        for (int i = 1; i < 256; i++) {
            cdfR[i] = cdfR[i - 1] + histR[i];
            cdfG[i] = cdfG[i - 1] + histG[i];
            cdfB[i] = cdfB[i - 1] + histB[i];
        }
        for (int i = 0; i < 256; i++) {
            cdfR[i] = cdfR[i] / totalPixels;
            cdfG[i] = cdfG[i] / totalPixels;
            cdfB[i] = cdfB[i] / totalPixels;
        }
        int[] mapR = new int[256];
        int[] mapG = new int[256];
        int[] mapB = new int[256];
        for (int i = 0; i < 256; i++) {
            mapR[i] = (int)(cdfR[i] * 255);
            mapG[i] = (int)(cdfG[i] * 255);
            mapB[i] = (int)(cdfB[i] * 255);
        }
        for (int i = 0; i < height; i++) {
            for (int j = 0; j < width; j++) {
                int[] rgb = getPixelArray(picture[i][j]);
                rgb[1] = mapR[rgb[1]];
                rgb[2] = mapG[rgb[2]];
                rgb[3] = mapB[rgb[3]];
                picture[i][j] = getPixels(rgb);
            }
        }
        resetPicture();
    }


  

  
  
  private void quit()
  {  
     System.exit(0);
  }

    @Override
   public void mouseEntered(MouseEvent m){}
    @Override
   public void mouseExited(MouseEvent m){}
    @Override
   public void mouseClicked(MouseEvent m){
        colorX = m.getX();
        colorY = m.getY();
        System.out.println(colorX + "  " + colorY);
        getValue();
        start.setEnabled(true);
    }
    @Override
   public void mousePressed(MouseEvent m){}
    @Override
   public void mouseReleased(MouseEvent m){}
   
   public static void main(String [] args)
   {
      IMP imp = new IMP();
   }
 
}