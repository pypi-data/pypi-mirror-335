def wallpaper():

    return [
        """
        <?xml version="1.0" encoding="utf-8"?>
        <LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
            android:layout_width="match_parent"
            android:layout_height="match_parent"
            android:gravity="center"
            android:orientation="vertical"
            android:padding="20dp">

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="CHANGING WALLPAPER APPLICATION"
                android:textSize="18sp"
                android:textStyle="bold"
                android:paddingBottom="20dp"/>

            <Button
                android:id="@+id/changeWallpaperButton"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="CLICK HERE TO CHANGE WALLPAPER"/>
        </LinearLayout>
        """,
        """
        package com.example.program5wallpaper;

        import android.app.WallpaperManager;
        import android.graphics.Bitmap;
        import android.graphics.BitmapFactory;
        import android.os.Bundle;
        import android.os.Handler;
        import android.view.View;
        import android.widget.Button;
        import android.widget.Toast;
        import androidx.appcompat.app.AppCompatActivity;
        import java.io.IOException;
        import java.util.Random;

        public class MainActivity extends AppCompatActivity {

            private Button changeWallpaperButton;
            private Handler handler = new Handler();
            private int[] wallpaperImages = {
                    R.drawable.wallpaper1,
                    R.drawable.wallpaper2,
                    R.drawable.wallpaper3,
                    R.drawable.wallpaper4
            };
            private Random random = new Random();

            private Runnable changeWallpaperRunnable = new Runnable() {
                @Override
                public void run() {
                    changeWallpaper();
                    handler.postDelayed(this, 5000); // Repeat every 30 seconds
                }
            };

            @Override
            protected void onCreate(Bundle savedInstanceState) {
                super.onCreate(savedInstanceState);
                setContentView(R.layout.activity_main);

                changeWallpaperButton = findViewById(R.id.changeWallpaperButton);

                changeWallpaperButton.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        changeWallpaper();
                        handler.postDelayed(changeWallpaperRunnable, 5000); // Start auto-change
                        Toast.makeText(MainActivity.this, "Wallpaper will change every 30 seconds!", Toast.LENGTH_SHORT).show();
                    }
                });
            }

            private void changeWallpaper() {
                WallpaperManager wallpaperManager = WallpaperManager.getInstance(this);
                int randomIndex = random.nextInt(wallpaperImages.length);
                Bitmap bitmap = BitmapFactory.decodeResource(getResources(), wallpaperImages[randomIndex]);

                try {
                    wallpaperManager.setBitmap(bitmap);
                    Toast.makeText(this, "Wallpaper Changed!", Toast.LENGTH_SHORT).show();
                } catch (IOException e) {
                    e.printStackTrace();
                    Toast.makeText(this, "Error setting wallpaper", Toast.LENGTH_SHORT).show();
                }
            }
        }
        """
    ]