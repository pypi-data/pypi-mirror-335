def mediaplayer():
    return [
        """
        <?xml version="1.0" encoding="utf-8"?>
        <LinearLayout
            xmlns:android="http://schemas.android.com/apk/res/android"
            android:layout_width="match_parent"
            android:layout_height="match_parent"
            android:gravity="center"
            android:orientation="vertical"
            android:padding="20dp">

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Basic Media Player"
                android:textSize="22sp"
                android:textStyle="bold"
                android:layout_marginBottom="20dp"/>

            <Button
                android:id="@+id/btnPlay"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Play"/>

            <Button
                android:id="@+id/btnPause"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Pause"
                android:layout_marginTop="10dp"/>

            <Button
                android:id="@+id/btnStop"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Stop"
                android:layout_marginTop="10dp"/>

        </LinearLayout>
        """,
        """
        package com.example.program9mediaplayer;

        import android.media.MediaPlayer;
        import android.os.Bundle;
        import android.view.View;
        import android.widget.Button;
        import android.widget.Toast;
        import androidx.appcompat.app.AppCompatActivity;

        public class MainActivity extends AppCompatActivity {
            private MediaPlayer mediaPlayer;
            
            private Button btnPlay, btnPause, btnStop;

            @Override
            protected void onCreate(Bundle savedInstanceState) {
                super.onCreate(savedInstanceState);
                setContentView(R.layout.activity_main);

                btnPlay = findViewById(R.id.btnPlay);
                btnPause = findViewById(R.id.btnPause);
                btnStop = findViewById(R.id.btnStop);

                // Initialize MediaPlayer with an audio file (place audio in res/raw folder)
                mediaPlayer = MediaPlayer.create(this, R.raw.flute);

                btnPlay.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        if (!mediaPlayer.isPlaying()) {
                            mediaPlayer.start();
                            Toast.makeText(MainActivity.this, "Playing Audio", Toast.LENGTH_SHORT).show();
                        }
                    }
                });

                btnPause.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        if (mediaPlayer.isPlaying()) {
                            mediaPlayer.pause();
                            Toast.makeText(MainActivity.this, "Audio Paused", Toast.LENGTH_SHORT).show();
                        }
                    }
                });

                btnStop.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        if (mediaPlayer.isPlaying()) {
                            mediaPlayer.stop();
                            mediaPlayer.reset();
                            mediaPlayer = MediaPlayer.create(MainActivity.this, R.raw.flute);
                            Toast.makeText(MainActivity.this, "Audio Stopped", Toast.LENGTH_SHORT).show();
                        }
                    }
                });
            }

            @Override
            protected void onDestroy() {
                super.onDestroy();
                if (mediaPlayer != null) {
                    mediaPlayer.release();
                    mediaPlayer = null;
                }
            }
        }
        """,
        """AndroidManifest.xml""",
        """
        <?xml version="1.0" encoding="utf-8"?>
        <manifest xmlns:android="http://schemas.android.com/apk/res/android"
            xmlns:tools="http://schemas.android.com/tools">
            <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE"/>
            <uses-permission android:name="android.permission.INTERNET"/>
            <application
                android:allowBackup="true"
                android:dataExtractionRules="@xml/data_extraction_rules"
                android:fullBackupContent="@xml/backup_rules"
                android:icon="@mipmap/ic_launcher"
                android:label="@string/app_name"
                android:roundIcon="@mipmap/ic_launcher_round"
                android:supportsRtl="true"
                android:theme="@style/Theme.Program9MediaPlayer"
                tools:targetApi="31">
                <activity
                    android:name=".MainActivity"
                    android:exported="true">
                    <intent-filter>
                        <action android:name="android.intent.action.MAIN" />
                        <category android:name="android.intent.category.LAUNCHER" />
                    </intent-filter>
                </activity>
            </application>

        </manifest>
        """
    ]